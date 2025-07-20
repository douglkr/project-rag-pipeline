import logging
import torch
import base64
from io import BytesIO
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info

logger = logging.getLogger(__name__)

class Qwen:
    def __init__(self, model_name, device_map, attn_implementation, min_pixels, max_pixels):
        """Load the model and processor"""
        logger.info(
            f"Initializing Qwen with model '{model_name}', device '{device_map}', "
            f"attention implementation '{attn_implementation}', "
            f"min_pixels {min_pixels}, "
            f"max_pixels {max_pixels} "
        )

        self.model_name = model_name
        self.device_map = device_map
        self.attn_implementation = attn_implementation
        self.min_pixels = min_pixels
        self.max_pixels = max_pixels

        try:
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                device_map=self.device_map,
                attn_implementation=self.attn_implementation
            )
            self.processor = AutoProcessor.from_pretrained(
                self.model_name, 
                min_pixels=self.min_pixels, 
                max_pixels=self.max_pixels
            )
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load model.")
            raise
    
    def query_images(self, query, images, max_tokens_output):
        """Generate a textual response to the query (text) based on the information in the supplied list of PIL images."""
        content = []
        try:
            logger.info("Processing images.")
            for img in images:
                buffer = BytesIO()
                img.save(buffer, format="jpeg")
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                content.append({"type": "image", "image": f"data:image;base64,{img_base64}"})

            content.append({"type": "text", "text": query})
            messages = [{"role": "user", "content": content}]

            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.device_map)
            logger.info("Images processed successfully.")

            logger.info("Generating output.")
            # Inference: Generation of the output.
            generated_ids = self.model.generate(**inputs, max_new_tokens=max_tokens_output)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            logger.info("Output generated successfully.")
            return self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0] 
        except Exception as e:
            logger.exception("Failed to generate text.")
            raise
