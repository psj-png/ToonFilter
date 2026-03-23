import cv2
import numpy as np


def render_cartoon_interactive(image_path):
    img = cv2.imread(image_path)
    if img is None: return

    saturation_scale = 1.0
    edge_block_size = 9

    is_recording = False
    video_writer = None
    h, w = img.shape[:2]

    while True:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] *= saturation_scale
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        img_colored = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        gray = cv2.cvtColor(img_colored, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, edge_block_size, 9)

        color = cv2.bilateralFilter(img_colored, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)

        info_text = f"Sat: {saturation_scale:.1f} | Edge Size: {edge_block_size}"
        cv2.putText(cartoon, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if is_recording:
            cv2.circle(cartoon, (w - 30, 30), 10, (0, 0, 255), -1)
            cv2.putText(cartoon, "REC", (w - 85, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            video_writer.write(cartoon)

        cv2.imshow("Cartoon Rendering", cartoon)

        key = cv2.waitKeyEx(1)

        if key == ord(' '):
            if not is_recording:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter('output.mp4', fourcc, 20.0, (w, h))
                is_recording = True
            else:
                is_recording = False
                video_writer.release()

        elif key == ord('c') or key == ord('C'):
            saturation_scale += 0.1
        elif key == ord('d') or key == ord('D'):
            saturation_scale = max(0.0, saturation_scale - 0.1)
        elif key == 0x260000:
            edge_block_size += 2
        elif key == 0x280000:
            edge_block_size = max(3, edge_block_size - 2)
        elif key == 27:
            if is_recording:
                video_writer.release()

            save_name = image_path.split('.')[0] + "_result.png"
            cv2.imwrite(save_name, cartoon)
            break

    cv2.destroyAllWindows()


render_cartoon_interactive('nature.png')