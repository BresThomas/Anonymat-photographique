#!/usr/bin/env python3
import os
import sys
import json
from simple_image import Image
from math import floor, ceil

def read_orders_from_json(json_filename):
    """Lit et retourne les ordres depuis le fichier JSON nommé
    `json_filename`."""
    print(f"Lecture du fichier d'ordres '{json_filename}'.")
    with open(json_filename, 'r') as f:
        orders = json.load(f)
    # on vérifie la présence des 3 clés de base (et uniquement elles) et
    # le type de valeurs associées
    for key in orders.keys():
        if key not in ["out", "in", "shapes"]:
            print(f"** Clé '{key}' inconnue")
    if "in" not in orders.keys() or not isinstance(orders["in"], str):
        print("** La clé 'in' doit être le nom du fichier image à lire")
        sys.exit(1)
    if "out" not in orders.keys() or not isinstance(orders["out"], str):
        print("** La clé 'out' doit être le nom du fichier image à produire")
        sys.exit(1)
    if "shapes" not in orders.keys() or not isinstance(orders["shapes"], list):
        print("** La clé 'shapes' doit être une liste de formes à flouter")
        sys.exit(1)
    # pour chaque type de formes on vérifie la présence des clés
    # attendues
    for shape in orders["shapes"]:
        if "type" not in shape.keys():
            print("** Une forme doit définir la clé 'type'")
            sys.exit(1)
        if shape["type"] == "circle":
            # les clés fournies ont-elles les noms attendus ?
            for key in shape.keys():
                if key not in ["type", "x", "y", "r"]:
                    print(f"** Clé '{key}' inconnue pour une forme 'circle'")
                    sys.exit(1)
            # les clés attendues sont-elles présentes avec des valeurs
            # du bon type (des entiers ou des réels) ?
            for key in ["x", "y", "r"]:
                if (key not in shape.keys() or not isinstance(shape[key], (int, float))):
                    print(f"La clé '{key}' d'un 'circle' doit être un nombre")
                    sys.exit(1)
        elif shape["type"] == "rectangle":
            # Les clés fournies ont-elles les noms attendus pour un rectangle ?
            for key in shape.keys():
                if key not in ["type", "c1x", "c1y", "c2x", "c2y"]:
                    print(f"** Clé '{key}' inconnue pour une forme 'rectangle'")
                    sys.exit(1)
            # Les clés attendues sont-elles présentes avec des valeurs
            # du bon type (des entiers ou des réels) ?
            for key in ["c1x", "c1y", "c2x", "c2y"]:
                if (key not in shape.keys() or not isinstance(shape[key], (int, float))):
                    print(f"La clé '{key}' d'un 'rectangle' doit être un nombre")
                    sys.exit(1)
        elif shape["type"] == "ellipse":
            # Les clés fournies ont-elles les noms attendus pour une ellipse ?
            for key in shape.keys():
                if key not in ["type", "x", "y", "a", "b"]:
                    print(f"** Clé '{key}' inconnue pour une forme 'ellipse'")
                    sys.exit(1)
            # Les clés attendues sont-elles présentes avec des valeurs
            # du bon type (des entiers ou des réels) ?
            for key in ["x", "y", "a", "b"]:
                if (key not in shape.keys() or not isinstance(shape[key], (int, float))):
                    print(f"La clé '{key}' d'une 'ellipse' doit être un nombre")
                    sys.exit(1)
        else:
            print(f"** Forme '{shape['type']}' inconnue !")

    # on retrouve le chemin d'accès des images `in` et `out`
    # relativement au chemin d'accès du fichier JSON
    dirname = os.path.dirname(json_filename)
    orders["in"] = os.path.join(dirname, orders["in"])
    orders["out"] = os.path.join(dirname, orders["out"])
    return orders

def clone_image(im):
    """Permet de cloner une image."""
    res = Image.new(width=im.width, height=im.height)
    for x in range(im.width):
        for y in range(im.height):
            (r, g, b) = im.get_color((x, y))
            res.set_color((x, y), (r, g, b))
    return res

def average_color_circle(im, cxy, cr):
    """Calculer la couleur moyenne du cercle dans l'image."""
    centerX, centerY = cxy
    total_color = [0, 0, 0]
    num_pixels = 0
    for x in range(floor(centerX - cr), ceil(centerX + cr)):
        for y in range(floor(centerY - cr), ceil(centerY + cr)):
            if (x - centerX) ** 2 + (y - centerY) ** 2 <= cr ** 2:
                try:
                    color = im.get_color((x, y))
                    total_color[0] += color[0]
                    total_color[1] += color[1]
                    total_color[2] += color[2]
                    num_pixels += 1
                except ValueError:
                    pass  # Ignore pixels outside the image

    if num_pixels > 0:
        average_color = (
            total_color[0] // num_pixels,
            total_color[1] // num_pixels,
            total_color[2] // num_pixels,
        )
        return average_color
    else:
        # Return black if no valid pixels found
        return (0, 0, 0)

def fill_circle(im, cxy, cr, color):
    """Remplir le cercle dans l'image avec la couleur spécifiée."""
    centerX, centerY = cxy

    for x in range(floor(centerX - cr), ceil(centerX + cr)):
        for y in range(floor(centerY - cr), ceil(centerY + cr)):
            # Ignorer les pixels en dehors de l'image
            if 0 <= x < im.width and 0 <= y < im.height:
                if (x - centerX) ** 2 + (y - centerY) ** 2 <= cr ** 2:
                    im.set_color((x, y), color)

def average_color_rectangle(im, c1xy, c2xy):
    """Calculer la couleur moyenne du rectangle dans l'image."""
    c1x, c1y = c1xy
    c2x, c2y = c2xy
    total_color = [0, 0, 0]
    num_pixels = 0
    for x in range(floor(c1x), ceil(c2x)):
        for y in range(floor(c1y), ceil(c2y)):
            try:
                color = im.get_color((x, y))
                total_color[0] += color[0]
                total_color[1] += color[1]
                total_color[2] += color[2]
                num_pixels += 1
            except ValueError:
                pass  # Ignore pixels outside the image

    if num_pixels > 0:
        average_color = (
            total_color[0] // num_pixels,
            total_color[1] // num_pixels,
            total_color[2] // num_pixels,
        )
        return average_color
    else:
        # Return black if no valid pixels found
        return (0, 0, 0)

def fill_rectangle(im, c1xy, c2xy, color):
    """Remplir le rectangle dans l'image avec la couleur spécifiée."""
    c1x, c1y = c1xy
    c2x, c2y = c2xy

    for x in range(floor(c1x), ceil(c2x)):
        for y in range(floor(c1y), ceil(c2y)):
            # Ignorer les pixels en dehors de l'image
            if 0 <= x < im.width and 0 <= y < im.height:
                im.set_color((x, y), color)

def average_color_ellipse(im, cxy, a, b):
    """Calculer la couleur moyenne de l'ellipse dans l'image."""
    centerX, centerY = cxy
    total_color = [0, 0, 0]
    num_pixels = 0
    for x in range(floor(centerX - a), ceil(centerX + a)):
        for y in range(floor(centerY - b), ceil(centerY + b)):
            if ((x - centerX) ** 2 / (a ** 2)) + ((y - centerY) ** 2 / (b ** 2)) <= 1:
                try:
                    color = im.get_color((x, y))
                    total_color[0] += color[0]
                    total_color[1] += color[1]
                    total_color[2] += color[2]
                    num_pixels += 1
                except ValueError:
                    pass  # Ignore pixels outside the image

    if num_pixels > 0:
        average_color = (
            total_color[0] // num_pixels,
            total_color[1] // num_pixels,
            total_color[2] // num_pixels,
        )
        return average_color
    else:
        # Return black if no valid pixels found
        return (0, 0, 0)

def fill_ellipse(im, cxy, a, b, color):
    """Remplir l'ellipse dans l'image avec la couleur spécifiée."""
    centerX, centerY = cxy

    for x in range(floor(centerX - a), ceil(centerX + a)):
        for y in range(floor(centerY - b), ceil(centerY + b)):
            # Ignorer les pixels en dehors de l'image
            if 0 <= x < im.width and 0 <= y < im.height:
                if ((x - centerX) ** 2 / (a ** 2)) + ((y - centerY) ** 2 / (b ** 2)) <= 1:
                    im.set_color((x, y), color)

def exec_orders(orders):
    """Exécute les ordres spécifiés dans le fichier d'ordres."""
    im_in = Image.read(orders["in"])
    im_out = clone_image(im_in)


    for shape in orders["shapes"]:
        if shape["type"] == "circle":
            cxy = (shape["x"], shape["y"])
            cr = shape["r"]
            color = average_color_circle(im_in, cxy, cr)
            fill_circle(im_out, cxy, cr, color)
        elif shape["type"] == "rectangle":
            c1xy = (shape["c1x"], shape["c1y"])
            c2xy = (shape["c2x"], shape["c2y"])
            color = average_color_rectangle(im_in, c1xy, c2xy)
            fill_rectangle(im_out, c1xy, c2xy, color)
        elif shape["type"] == "ellipse":
            cxy = (shape["x"], shape["y"])
            a = shape["a"]
            b = shape["b"]
            color = average_color_ellipse(im_in, cxy, a, b)
            fill_ellipse(im_out, cxy, a, b, color)

    im_out.save(orders["out"])
    print(f"Image enregistrée sous '{orders['out']}'.")

def main():
    """Programme principale qui lit ou demande un fichier d'ordres puis
    les exécute."""
    if len(sys.argv) == 2:
        orders_filename = sys.argv[1]
    else:
        orders_filename = input("Nom du fichier d'ordres: ")

    orders = read_orders_from_json(orders_filename)
    exec_orders(orders)

if __name__ == "__main__":
    main()
