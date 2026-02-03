# ComfyUI-BJNodes / Veo Prompt Helper (Final)

import os
import re
import folder_paths

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except:
    CLIPBOARD_AVAILABLE = False


# -------------------------------------------------
# Prompt Builder
# -------------------------------------------------
class PromptBuilder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "person": ("STRING", {"multiline": True}),
                "background": ("STRING", {"multiline": True}),
                "era_background": ("STRING", {"multiline": True}),
                "timeline_actions": ("STRING", {"multiline": True}),
                "constraints": ("STRING", {"multiline": True}),

                # Style checkboxes
                "style_realistic": ("BOOLEAN", {"default": True}),
                "style_cinematic": ("BOOLEAN", {"default": True}),
                "style_documentary": ("BOOLEAN", {"default": False}),
                "style_epic_fantasy": ("BOOLEAN", {"default": False}),
                "style_handheld_realism": ("BOOLEAN", {"default": False}),

                "time_preset": ([
                    "none",
                    "morning, soft natural daylight",
                    "midday, neutral daylight",
                    "sunset, warm golden hour light",
                    "night, cinematic low light",
                    "dark indoor environment",
                    "bright indoor lighting",
                ],),

                "camera_preset": ([
                    "none",
                    "static",
                    "handheld",
                    "zoom in",
                    "zoom out",
                    "camera follows",
                    "pan left",
                    "pan right",
                    "tilt up",
                    "tilt down",
                    "orbit around",
                    "dolly in",
                    "dolly out",
                    "dolly left",
                    "dolly right",
                    "jib up",
                    "jib down",
                    "drone shot",
                    "360 roll",
                ],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("structured_prompt",)
    FUNCTION = "build"
    CATEGORY = "ComfyUI-BJNodes"

    def build(
        self,
        person,
        background,
        era_background,
        timeline_actions,
        constraints,
        style_realistic,
        style_cinematic,
        style_documentary,
        style_epic_fantasy,
        style_handheld_realism,
        time_preset,
        camera_preset,
    ):
        styles = []
        if style_realistic:
            styles.append("realistic style with natural motion and real-world physics")
        if style_cinematic:
            styles.append("cinematic style with dramatic lighting and shallow depth of field")
        if style_documentary:
            styles.append("documentary style with observational camera work")
        if style_epic_fantasy:
            styles.append("epic fantasy style with dramatic scale and stylized realism")
        if style_handheld_realism:
            styles.append("handheld realism with natural camera imperfections")

        style_text = ", ".join(styles)

        text = f"""
<STYLE>{style_text}</STYLE>
<PERSON>{person}</PERSON>
<BACKGROUND>{background}</BACKGROUND>
<ERA>{era_background}</ERA>
<TIME>{time_preset}</TIME>
<CAMERA>{camera_preset}</CAMERA>
<TIMELINE>{timeline_actions}</TIMELINE>
<CONSTRAINTS>{constraints}</CONSTRAINTS>
"""
        return (text.strip(),)


# -------------------------------------------------
# Final Composer (Veo3 + Save + Clipboard)
# -------------------------------------------------
class PromptFinalComposer:
    OUTPUT_NODE = True  # ▶ 플레이 버튼 활성화

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "structured_prompt": ("STRING", {"multiline": True}),
                "cut_number": ("INT", {"default": 1, "min": 1}),
                "save_to_txt": ("BOOLEAN", {"default": False}),
                "copy_to_clipboard": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("final_prompt",)
    FUNCTION = "compose"
    CATEGORY = "ComfyUI-BJNodes"

    def extract(self, tag, text):
        m = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.S)
        return m.group(1).strip() if m else ""

    def camera_sentence(self, preset):
        mapping = {
            "static": "The camera remains static with stable framing.",
            "handheld": "The camera is handheld with subtle natural movement.",
            "zoom in": "The camera slowly zooms in toward the subject.",
            "zoom out": "The camera slowly zooms out to reveal more of the scene.",
            "camera follows": "The camera smoothly follows the subject's movement.",
            "pan left": "The camera pans left smoothly.",
            "pan right": "The camera pans right smoothly.",
            "tilt up": "The camera tilts upward to reveal vertical space.",
            "tilt down": "The camera tilts downward toward the subject.",
            "orbit around": "The camera slowly orbits around the subject.",
            "dolly in": "The camera dollies in smoothly toward the subject.",
            "dolly out": "The camera dollies out smoothly.",
            "dolly left": "The camera dollies left smoothly.",
            "dolly right": "The camera dollies right smoothly.",
            "jib up": "The camera rises upward using a jib movement.",
            "jib down": "The camera moves downward using a jib movement.",
            "drone shot": "The scene is captured as a smooth aerial drone shot.",
            "360 roll": "The camera performs a slow 360-degree roll.",
        }
        return mapping.get(preset, "")

    def compose(
        self,
        structured_prompt,
        cut_number,
        save_to_txt,
        copy_to_clipboard,
    ):
        style = self.extract("STYLE", structured_prompt)
        person = self.extract("PERSON", structured_prompt)
        background = self.extract("BACKGROUND", structured_prompt)
        era = self.extract("ERA", structured_prompt)
        time = self.extract("TIME", structured_prompt)
        camera = self.extract("CAMERA", structured_prompt)
        timeline = self.extract("TIMELINE", structured_prompt)
        constraints = self.extract("CONSTRAINTS", structured_prompt)

        camera_text = self.camera_sentence(camera)

        final_prompt = (
            f"{style}. "
            f"{person} "
            f"The environment is {background}. "
            f"The setting reflects {era}. "
            f"The scene takes place in {time}. "
            f"{camera_text} "
            f"{timeline} "
            f"{constraints} "
            f"The video follows realistic timing, natural motion, and smooth transitions."
        ).strip()

        if save_to_txt:
            base_dir = folder_paths.get_output_directory()
            out_dir = os.path.join(base_dir, f"cut_{cut_number:03d}")
            os.makedirs(out_dir, exist_ok=True)

            file_path = os.path.join(out_dir, "veo_prompt.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_prompt)

        if copy_to_clipboard and CLIPBOARD_AVAILABLE:
            pyperclip.copy(final_prompt)

        return (final_prompt,)


# -------------------------------------------------
# Node mappings
# -------------------------------------------------
NODE_CLASS_MAPPINGS = {
    "Prompt Builder": PromptBuilder,
    "Prompt Final Composer": PromptFinalComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Prompt Builder": "Prompt Builder",
    "Prompt Final Composer": "Prompt Final Composer (Veo3 + Save + Clipboard)",
}
