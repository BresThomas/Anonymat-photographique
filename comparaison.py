import cv2

def calculate_image_similarity(image_path1, image_path2):
    try:
        # Charger les images en niveaux de gris
        img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

        # Calculer l'histogramme des couleurs
        hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])

        # Calculer la similarité entre les deux histogrammes
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        # La similarité est un nombre entre -1 et 1, plus proche de 1 signifie plus similaire
        return similarity
    except Exception as e:
        print(f"Error: {e}")
        return 0.0

if __name__ == "__main__":
    image_path1 = "images/chats-flou.png"
    image_path2 = "images-reference/chats-flou.png"

    similarity = calculate_image_similarity(image_path1, image_path2)

    print(f"Similarity between images: {similarity}")
