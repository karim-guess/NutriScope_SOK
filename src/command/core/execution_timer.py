import time
from datetime import datetime

class ExecutionTimer:
    def __init__(self):
        self.start_time = None

    def log_start(self) -> None:
        self.start_time = time.time()
        self.log_step("Démarrage du traitement...")

    def log_step(self, message: str) -> None:
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"[{time_str}] {message}")

    def log_end(self, message: str = "") -> None:
        if self.start_time is None:
            print("Erreur : Le timer n'a pas été démarré avec log_start().")
            return

        end_time = time.time()
        execution_time = end_time - self.start_time
        minutes = int(execution_time // 60)
        seconds = int(execution_time % 60)

        print(f"✅ Terminé avec succès ! {message}")
        print(f"Temps d'exécution total : {minutes} min {seconds} s (soit {execution_time:.2f} secondes).")