import os
import cv2
import concurrent.futures
from time import sleep


class ImageAugmentor:
    def __init__(self, sample_path):
        self.sample_path = sample_path
        try:
            os.chdir(self.sample_path)
        except Exception as ex:
            print(ex)
            return
        try:
            os.mkdir(self.sample_path + r"\augmented")
        except FileExistsError:
            pass
        self.augmented_path = self.sample_path + r"\augmented"
        self.images = [
            name
            for name in os.listdir(self.sample_path)
            if not os.path.isdir(os.path.join(self.sample_path, name))
        ]
        print(self.augmented_path)
        print(len(self.images))

    def augment_task(self, image: str, convert=True, rotate=True, flip=True):
        augmented_images = {}
        base_image = cv2.imread(os.path.join(self.sample_path, image))
        filename, ext = os.path.splitext(image)[0], os.path.splitext(image)[1]
        if rotate:
            image_90CW = cv2.rotate(base_image, cv2.cv2.ROTATE_90_CLOCKWISE)
            image_180 = cv2.rotate(base_image, cv2.ROTATE_180)
            image_90CCW = cv2.rotate(base_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            augmented_images[f"{filename}_90CW"] = image_90CW
            augmented_images[f"{filename}_180"] = image_180
            augmented_images[f"{filename}_90CCW"] = image_90CCW
        if flip:
            image_hor = cv2.flip(base_image, 1)
            image_vert_hor = cv2.flip(base_image, -1)
            augmented_images[f"{filename}_hor"] = image_hor
            if not rotate:
                augmented_images[f"{filename}_vert_hor"] = image_vert_hor
        for filename, image in augmented_images.items():
            if convert:
                cv2.imwrite(
                    fr"{self.sample_path}\augmented\{filename}.jpg",
                    image,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 100],
                )
                augmented_images[filename] = fr"{self.sample_path}\augmented\{filename}.jpg",
                print(fr"{self.sample_path}\augmented\{filename}.jpg",)
            else:
                cv2.imwrite(
                    fr"{self.augmented_path}\{filename}{ext}",
                    image,
                    [int(cv2.IMWRITE_JPEG_QUALITY), 100],
                )
                augmented_images[filename] = fr"{self.sample_path}\augmented\{filename}{ext}"
                print(fr"{self.sample_path}\augmented\{filename}{ext}")
            sleep(0.3)
        return augmented_images

    def augment(self, convert=True, rotate=True, flip=True):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_image = {
                executor.submit(self.augment_task, image): image
                for image in self.images
            }
        for future in concurrent.futures.as_completed(future_to_image):
            image = future_to_image[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f"{image} generated an exception {exc}")
            else:
                print(f"{image} rewritten path: {data}")


if __name__ == "__main__":
    ImageAugmentor(r"C:\Users\WinSys\Documents\gun classification\haar_cascade\p").augment()
