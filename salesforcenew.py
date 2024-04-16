import requests
import os
import shutil
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

def process_image(image_location,image_name):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

    img_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg' 
    raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')
    raw_image = Image.open(image_location).convert('RGB')


    # Unconditional image captioning
    inputs = processor(raw_image, return_tensors="pt")

    out = model.generate(**inputs)
    output = (processor.decode(out[0], skip_special_tokens=True))

    print(output)

    # Image generation
    base = "stabilityai/stable-diffusion-xl-base-1.0"
    repo = "ByteDance/SDXL-Lightning"
    ckpt = "sdxl_lightning_4step_unet.safetensors" 


    # Load model.
    unet = UNet2DConditionModel.from_config(base, subfolder="unet").to("cuda", torch.float16)
    unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device="cuda"))
    pipe = StableDiffusionXLPipeline.from_pretrained(base, unet=unet, torch_dtype=torch.float16, variant="fp16").to("cuda")


    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

    pipe(output, num_inference_steps=4, guidance_scale=0).images[0].save(image_name)
    shutil.move(image_name,"Static/generatedimages/"+image_name)
    """ if os.path.exists(image_location):
        os.remove(image_location)
    else:
     print(image_location)"""
