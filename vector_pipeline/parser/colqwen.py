import logging
import torch
from PIL import Image
import base64
from io import BytesIO
from colpali_engine.models import ColQwen2, ColQwen2Processor

logger = logging.getLogger(__name__)

class Colqwen:
    def __init__(self, model_name, device_map, attn_implementation):
        """Load the model and processor from huggingface."""
        logger.info(
            f"Initializing Colqwen with model '{model_name}', device '{device_map}', "
            f"attention implementation '{attn_implementation}'"
        )
        try:
            self.model = ColQwen2.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                device_map=device_map,
                attn_implementation=attn_implementation,
            ).eval()
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load model.")
            raise

        try:
            self.processor = ColQwen2Processor.from_pretrained(model_name)
            logger.info("Processor loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load processor.")
            raise

    @staticmethod
    def _base64_to_pil(base64_str: str) -> Image.Image:
        image_data = base64.b64decode(base64_str)
        return Image.open(BytesIO(image_data)).convert("RGB")

    def multi_vectorize_image(self, img_base64):
        """Accept base64-encoded image and return multi-vector embedding."""
        try:
            img = self._base64_to_pil(img_base64)
            image_batch = self.processor.process_images([img]).to(self.model.device)
            with torch.no_grad():
                image_embedding = self.model(**image_batch)
            return image_embedding[0]
        except Exception as e:
            logger.exception("Failed to vectorize base64 image.")
            raise

    def multi_vectorize_text(self, query):
        """Return the multi-vector embedding of the query text string."""
        logger.debug(f"Processing text query for vectorization: '{query}'")
        try:
            query_batch = self.processor.process_queries([query]).to(self.model.device)
            logger.debug("Text query batch processed and moved to device.")
            with torch.no_grad():
                query_embedding = self.model(**query_batch)
            logger.info("Text successfully vectorized.")
            return query_embedding[0]
        except Exception as e:
            logger.exception("Failed to vectorize text.")
            raise

    def maxsim(self, query_embedding, image_embedding):
        """Compute the MaxSim between the query and image multi-vectors."""
        logger.debug("Computing MaxSim score between query and image embeddings.")
        try:
            score = self.processor.score_multi_vector(
                [query_embedding], [image_embedding]
            ).item()
            logger.info(f"MaxSim score computed: {score}")
            return score
        except Exception as e:
            logger.exception("Failed to compute MaxSim score.")
            raise