import subprocess
import time


class OllamaController:

    def __init__(self):
        self.active_model = None


    def start_model(self, model_name):

        if self.active_model:
            self.stop_model()

        print(f"START MODEL: {model_name}")

        self.active_model = model_name

        self.process = subprocess.Popen(
            [
                "ollama",
                "run",
                model_name
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(3)


    def send_prompt(self, prompt):

        if not self.active_model:
            raise Exception(
                "Brak aktywnego modelu"
            )

        print(
            f"Wysyłam do {self.active_model}:"
        )

        output, error = self.process.communicate(
            prompt
        )

        return output


    def stop_model(self):

        if self.active_model:

            print(
                f"STOP MODEL: {self.active_model}"
            )

            self.process.kill()

            self.active_model = None



if __name__ == "__main__":

    controller = OllamaController()

    controller.start_model(
        "qwen2.5:7b"
    )

    controller.stop_model()

    controller.start_model(
        "qwen2.5-coder:7b"
    )

    controller.stop_model()