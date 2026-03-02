class GestureDetector:
    def __init__(self):
        pass

    def is_one_finger(self, landmarks):
        if len(landmarks) != 21:
            return False

        index_open = landmarks[8][1] < landmarks[6][1]
        middle_closed = landmarks[12][1] > landmarks[10][1]
        ring_closed = landmarks[16][1] > landmarks[14][1]
        pinky_closed = landmarks[20][1] > landmarks[18][1]

        return index_open and middle_closed and ring_closed and pinky_closed

    def is_hand_open(self, landmarks):
        """Eğer 3 veya daha fazla parmak açık ise, el açık olarak kabul edilir."""
        if len(landmarks) != 21:
            return False 
        fingers_open = 0

        fingers_ids = [8,12,16,20]  # Başparmak, işaret parmağı, orta parmak, yüzük parmağı
        pip_ids = [6,10,14,18]  # Başparmak, işaret parmağı, orta parmak, yüzük parmağı

        for tip_id, pip_id in zip(fingers_ids, pip_ids):
            if landmarks[tip_id][1] < landmarks[pip_id][1]:  # Parmak ucu, pip ekleminden yukarıda mı?
                fingers_open += 1
        return fingers_open >= 3
    
    def is_fist(self, landmarks):
        if len(landmarks) != 21:
            return False
        fingers_ids = [8, 12, 16, 20]  # İşaret parmağı, orta parmak, yüzük parmağı, küçük parmak
        pip_ids = [6, 10, 14, 18]  # PIP eklemleri

        for tip_id, pip_id in zip(fingers_ids, pip_ids):
            if landmarks[tip_id][1] < landmarks[pip_id][1]:  # Parmak ucu, pip ekleminden yukarıda mı?
                return False     
            
        return True