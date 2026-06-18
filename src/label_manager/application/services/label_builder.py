class LabelBuilder:

    @staticmethod
    def build(text: str = "Hola Mundo", qr_data: str | None = None, copies: int = 1) -> str:
        zpl = "^XA\n"
        zpl += f"^PQ{copies}\n"
        zpl += f"^FO50,50^A0N,40,40^FD{text}^FS\n"
        if qr_data:
            zpl += f"^FO50,150^BQN,2,10^FD{qr_data}^FS\n"
        zpl += "^XZ"
        return zpl
