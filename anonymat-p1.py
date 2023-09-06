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
            print("** Clé '{key}' inconnue")
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

def exec_orders(orders):
    """Exécute les ordres `orders`..."""
    print("Image à lire:", orders["in"])
    im_in = Image.read(orders["in"])
    im_out = clone_image(im_in)

    if len(orders["shapes"]) == 0:
        print("Pas de formes à flouter")
    else:
        print("Liste des formes à flouter:")
        for shape in orders["shapes"]:
            if shape["type"] == "circle":
                print(f"  Cercle de centre ({shape['x']}, {shape['y']}) de rayon {shape['r']}")

                # Calculer la couleur moyenne du cercle dans 'im_in'
                average_color = average_color_circle(im_in, (shape["x"], shape["y"]), shape["r"])

                # Appliquer cette couleur au cercle dans 'im_out'
                fill_circle(im_out, (shape["x"], shape["y"]), shape["r"], average_color)

            else:
                print(f"  ** Forme '{shape['type']}' inconnue !")
                print(f"  ** TODO: ajouter le traitement des formes de type '{shape['type']}'")

    print("Image à produire:", orders["out"])
    im_out.save(orders["out"])


def main():
    """Programme principal qui lit ou demande un fichier d'ordres puis
    les exécute."""
    if len(sys.argv) == 2:
        orders_filename = sys.argv[1]
    else:
        orders_filename = input("Nom du fichier d'ordres: ")

    orders = read_orders_from_json(orders_filename)
    exec_orders(orders)

if __name__ == "__main__":
    main()
