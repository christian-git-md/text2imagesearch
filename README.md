## Overview
This repo provides a simple way to construct and query a text / image vector database to search for images that are related to text. 

The image and text embeddings are both calculated from a huggingface [implementation](https://huggingface.co/docs/transformers/model_doc/clip) of the clip model. I use the pre-trained model files of the `clip-vit-base-patch32` model, without any modifications. The important part in the query processing - (approximate nearest neighbor search) - is handled by [qdrant](https://qdrant.tech/).
## Prerequisites
- machine with gpu
- nvidia-docker
- stable internet connection for model downloads

## Setup
Build the docker images:

```bash
docker pull qdrant/qdrant
cd model_serving/docker
docker build . -t model_serving
cd ../..
cd text2image/docker
docker build . -t text2image
cd ../..
```

Run the containers from this repo's root directory:
```bash
# Qdrant server
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant

# Model serving
docker run \
 --gpus all \
 -v $(pwd)/model_serving:/model_serving \
 -w /model_serving \
 -p 9090:9090 \
 model_serving:latest
 
# Text2image app
docker run \
 -it \
 --gpus all \
 -v $(pwd)/text2image:/text2image \
 -w /text2image \
 -p 9091:9091 \
 text2image:latest bash
```

Optionally add the snapshot of already infered coco_val (4000 images) vectors to the qdrant server. [download link](https://drive.google.com/file/d/1_U9tvvfKaqQ6QgziWgLECSOye_Ul43Wo/view?usp=drive_link). Upload the snapshot in the gui at http://0.0.0.0:6333/dashboard, and name the collection `coco_val`.

<img src="https://i.imgur.com/uME1kEQ.png" height="200">

See [here](https://qdrant.tech/documentation/tutorials/create-snapshot/) for more info on how to restore from a snapshot.

## Usage
The api has 2 functionalities:
1) Consume an image URL. Calculate embedding for a new image and add it to the vector database
2) Consume some text. Find the top matching images from the database that match this embedding, and return the URL.

### Add image
If you have a valid image url, you can add the embedding of that image to the database with a request like in `scripts/test_upload_image.py`:
```python
url = "http://0.0.0.0:9091/add-image"
data = {"image_url": "https://i.pinimg.com/474x/34/18/a6/3418a655e5f5784cd2539a6d9a8dbc3a.jpg"}
response = requests.post(url, data=data)
```
### Make Queries
After we uploaded the snapshot, or added some data manually, we can start to make queries with a request similar to `scripts/test_query_text.py`:
```python
url = "http://0.0.0.0:9091/"
data = {"text": "A black cat"}
response = requests.post(url, data=data)
```

For example if we run with the query "A black cat" we will receive 5 urls of images of black cats:

<img src="https://upload.wikimedia.org/wikipedia/commons/4/4c/Blackcat-Lilith.jpg" height="100"> <img src="http://images.cocodataset.org/val2017/000000304560.jpg" height="100"> <img src="http://images.cocodataset.org/val2017/000000153217.jpg" height="100"> <img src="http://images.cocodataset.org/val2017/000000501523.jpg" height="100"> <img src="http://images.cocodataset.org/val2017/000000284623.jpg" height="100">

Of course, we are limited by the variety of the images that we have added to our database. If we search for something really specific, like a woman in a pink dress dancing in the rain, we will only find vaguely related images:

<img src="http://images.cocodataset.org/val2017/000000402774.jpg" height="100"> <img src="http://images.cocodataset.org/val2017/000000408120.jpg" height="100"> <img src="http://images.cocodataset.org/val2017/000000122046.jpg" height="100"> <img src="http://images.cocodataset.org/val2017/000000333745.jpg" height="100">

However, if we add the vector of such an image using the `/add-image` endpoint, this image will indeed be our top result:

<img src="https://i.pinimg.com/474x/34/18/a6/3418a655e5f5784cd2539a6d9a8dbc3a.jpg" height="200">

See [more_examples.md](more_examples.md) for more examples, also illustrating some failure cases.

## App Configuration
Some configuration can be made in text2image/appconfig, such as the number of results and the default qdrant collection name.

## Dataset

I use the validation part of the coco dataset for this demo, as it has nice variety and already existing access to images via URLs. This dataset likely has some shortcomings in terms of coverage, since the images have been selected with some biases (contains mostly close-up photography of well-defined objects). [Here](https://openai.com/research/clip) is some interesting evaluation of the openai clip model that suggests that it has a significantly higher degree of generalization to different domains than models that have been trained on imagenet data.

## Evaluation

Evaluation for this complete system is not easy, and there are many different ways in which the quality of a retrieval may be evaluated. Here is one suggestion:
- Take an evaluation dataset of images that are annotated with description. Calculate how high the image with the "real" description ranks.

However this method has some problems. Mainly, there might be other images in the dataset that match the description better than the original image. It might be easier to evaluate model performance and retrieval individually instead.
- For the model we can follow e.g. the evaluation metrics from the clip paper
- The ranking should ideally retrieve the images with the highest relevance (based on the model outputs).We can use e.g. mAP to calculate our ranking vs the "true ranking".

## Potential Improvements
The code in this repository is not refined and the apis could use more data validation, documentation and some cleanup of the model serving. We could achieve more efficient model inference by utilizing the batch processing of images.

In terms of performance, the first obvious improvement to make is to add a bigger dataset, with more variety to provide more potential matches. Since every image only needs to be evaluated a single time, and there is a large corpus of training data availible (from the internet), a deeper model is likely a good idea.

We could use [synonym substitution](https://arxiv.org/pdf/2401.01830.pdf) to force more diverse results (and thus increase the chance for a top-n match). In [more_examples.md](more_examples.md) we have a case where "singer" is associated with bird strongly enough to only receive bird images in the top 5 from the coco dataset. In this case we would receive an arguably more fitting result by replacing "singer" with "vocalist":

<img src="http://images.cocodataset.org/val2017/000000411953.jpg" height="200">
