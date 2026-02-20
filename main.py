import cv2
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from game_logic import Player

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    detector = GestureDetector()
    player = Player()

    while True:
        succes, frame = cap.read()
        if not succes:
            break

        frame = cv2.flip(frame, 1)
        frame, landmarks = tracker.process_frame(frame)
        jump = detector.is_hand_open(landmarks)
        player.update(jump)
        player.draw(frame)

        if detector.is_hand_open(landmarks):
            cv2.putText(frame, "JUMP!", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2, (0, 255, 0), 3)

        elif detector.is_fist(landmarks):
            cv2.putText(frame, "FIST", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                2, (0, 0, 255), 3)

        cv2.imshow('Vision Controlled Jump Game', frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC tuşu
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()