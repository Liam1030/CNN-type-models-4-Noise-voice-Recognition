# CNN-type-models-4-Noise-voice-Recognition
Real-time Noise-voice recognition task with CNN-type models

## Dataset:
**Noise**: self labeled noises from webist freesound. Including several common noises appeared in online meeting: crowd, dog, keyboard, lawnmower, mouse click, passing car</br>
**Voice**: additive noise type noisy voice generated by mixing noise above with clean voice sampled from clean dataset Aurora4

## Models:
CNN-type pytorch implemented models in paper https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43969.pdf</br>
</br>
With [MobileNet](https://arxiv.org/pdf/1704.04861.pdf) Tricks applied, so that models may be more reasonable applied in real-time tasks. (Still needs more data to let this trick work)

## Packages Required:
**tensorflow** version >= 1.8.0 used for audio data preprocessing</br>
**pytorch** used for model training

## Run codes:
**training**: python3 train.py [model name] </br>
**testing**: python3 test.py [model name] [percentage of whole test data want to use]

## Performance:

![](https://user-images.githubusercontent.com/20760190/40931609-7ea3f31c-67e0-11e8-9d68-2278718d9194.png)

## Details:
For more details, please check out in this ![slides](https://www.sharelatex.com/read/zfyyzsjgykcr)
