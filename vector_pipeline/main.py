import logging
import os
from util.logging_config import setup_logging
from util.download_pdf import download_pdf_from_s3
from util.pdf_util import PDFImageConverter
from util.load_config import load_config
from parser.colqwen import Colqwen
from vector_store.weaviate import WeaviateCollectionManager

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting pipeline")

    # Read env variables from EventBridge
    logger.info("Reading env variables")
    bucket = os.environ.get("S3_BUCKET")
    key = os.environ.get("S3_KEY")
    logger.info(f"Bucket: {bucket} - key: {key}")

    try:
        # Load config
        config = load_config("config.yaml")

        # Download PDF
        pdf_path = download_pdf_from_s3(bucket, key)

        # Convert PDF to base64 images with metadata
        converter = PDFImageConverter(pdf_path, config)
        base64_images = converter.convert_to_base64_images()

        logger.info(f"Extracted {len(base64_images)} pages from PDF.")

        # Initialize model
        model = Colqwen(
            model_name=config["pdf_parser"]["model_specs"]["model_name"], 
            device_map=config["pdf_parser"]["model_specs"]["device_map"], 
            attn_implementation=config["pdf_parser"]["model_specs"]["attn_implementation"]
        )

        # Setup Weaviate
        manager = WeaviateCollectionManager(config=config)
        manager.connect(
            connection_type=config["weaviate"]["connection"]["type"], 
            host=config["weaviate"]["connection"]["host"],
        )
        manager._create_collection_if_not_exists()

        # Process each page/image
        for element in base64_images:
            try:
                base64_img = element.get("base64_image")
                embedding = model.multi_vectorize_image(base64_img)

                # Convert tensor to list (safe for any device)
                embedding_list = embedding.detach().cpu().float().numpy().tolist()

                # Prepare properties based on config
                properties = {
                    prop["name"]: element.get(prop["name"], None)
                    for prop in config["weaviate"]["collection"]["properties"]
                }

                manager.insert_object(properties=properties, embedding=embedding_list)
                logger.info(f"Inserted page {element.get('page_number')} into Weaviate.")
            except Exception as e:
                logger.exception(f"Failed to process page {element.get('page_number')}: {e}")

    except Exception as pipeline_error:
        logger.exception(f"Pipeline failed: {pipeline_error}")

    finally:
        # Ensure the Weaviate client is closed properly
        if "manager" in locals() and hasattr(manager, "client") and manager.client is not None:
            try:
                manager.client.close()
                logger.info("Weaviate client connection closed.")
            except Exception as e:
                logger.warning(f"Failed to close Weaviate client cleanly: {e}")
