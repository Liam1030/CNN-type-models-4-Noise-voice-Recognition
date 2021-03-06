import os
from pydub import AudioSegment
from random import shuffle
import random

def getwavfilename(dir):
    return [f for f in os.listdir(dir) if '.wav' in f]

def slicewav(olddir,newdir,oldwav):
    audio = AudioSegment.from_wav(olddir+oldwav)
    t1,t2=0,len(audio)//1000
    oldname=oldwav.split('.')[0]
    while t1<t2:
        newname=oldname+'_'+str(t1)
        newAudio = audio[t1*1000:(t1+1)*1000]
        newAudio.export(newdir+newname+'.wav', format="wav")
        t1+=1
    return t2
def slicedir(olddir,newdir,oldfiles):
    for file in oldfiles:
        try:
            slicewav(olddir,newdir,file)
        except Exception as e:
            print (olddir,file)

def splitTrainTest(olddir,trainDir,testDir,ratio=0.8):
    if not os.path.exists(trainDir):
        print ('mkdir {}'.format(trainDir))
        print (os.system('mkdir {}'.format(trainDir)))
    if not os.path.exists(testDir):
        print ('mkdir {}'.format(testDir))
        print (os.system('mkdir {}'.format(testDir)))
    files=getwavfilename(olddir)
    
    shuffle(files)
    trainFiles=files[:int(len(files)*ratio)]
    testFiles=files[int(len(files)*ratio):]
    
    slicedir(olddir,trainDir,trainFiles)
    slicedir(olddir,testDir,testFiles)
    
       
def getAllnoise(processedDir,isTrain=True):
    if isTrain:
        tail='Train'
    else:
        tail='Test'
    allDir=[d+'/' for d in os.listdir(processedDir) if tail in d]
    allnoisefiles=[]
    for dir in allDir:
        fulldir=processedDir+dir
        noisefiles=[fulldir+f for f  in os.listdir(fulldir) if '.wav' in f]
        allnoisefiles+=noisefiles
    shuffle(allnoisefiles)
    return allnoisefiles
    

def slicecleanwav(olddir,newdir,oldwav,sampleNum=3):
    audio = AudioSegment.from_wav(olddir+oldwav)
    t1,t2=0,len(audio)//1000
    if t2>1:
        t1=random.choice(range(t2))
    if t2-t1>3:
        t1s=sorted(random.sample(range(t1,t2),sampleNum))
    else:
        t1s=range(t1,t2)
        
    oldname=oldwav.split('.')[0]
    for t1 in t1s:
        newname=oldname+'_'+str(t1)
        newAudio = audio[t1*1000:(t1+1)*1000]
        newAudio.export(newdir+newname+'.wav', format="wav")
        
    return len(t1s)    
    
    
    

def cleanwavPickTrainTest(cleanwavDir,cleanTrainDir,cleanTestDir,trainNum=100,testNum=50):
    if not os.path.exists(cleanTrainDir):
        print ('mkdir {}'.format(cleanTrainDir))
        print (os.system('mkdir {}'.format(cleanTrainDir)))
    if not os.path.exists(cleanTestDir):
        print ('mkdir {}'.format(cleanTestDir))
        print (os.system('mkdir {}'.format(cleanTestDir)))
        
    cleanwavfiles=[f for f in os.listdir(cleanwavDir) if '.wav' in f]
    trainFilespool,testFilespool=cleanwavfiles[:int(len(cleanwavfiles)*0.6)],cleanwavfiles[int(len(cleanwavfiles)*0.6):]
    shuffle(trainFilespool)
    shuffle(testFilespool)
    
    trainsliced,testsliced=0,0
    
    for trainfile in trainFilespool:
        if trainsliced<trainNum:
            trainsliced+=slicecleanwav(cleanwavDir,cleanTrainDir,trainfile)
        else:
            break
            
    for testfile in testFilespool:
        if testsliced<testNum:
            testsliced+=slicecleanwav(cleanwavDir,cleanTestDir,testfile)
        else:
            break
def caldbs(sound,wnd):
    dbs=[]
    
    for i in range(len(sound)//wnd):
        dbs.append(sound[i*wnd:(i+1)*wnd].dBFS)
    return dbs
    
def normalizeaudio(wavfile,wnd,target):
    sound = AudioSegment.from_file(wavfile)
    s= AudioSegment.empty()
    maxdb=max(caldbs(sound,wnd))
    gaindb=target-maxdb
    for i in range(len(sound)//wnd):
        s+=sound[i*wnd:(i+1)*wnd].apply_gain(gaindb)
    return s

def mixsoundnoisepair(soundfile,noisefile,wnd,soundDBTarget,snr=15):
    noiseDBTarget=soundDBTarget-snr
    sound=normalizeaudio(soundfile,wnd,soundDBTarget)
    noise=normalizeaudio(noisefile,wnd,noiseDBTarget)
    combined=sound.overlay(noise)
    return combined

def mixnoises_sounds(soundfiles,noisefiles,outputDir,wnd=10,soundDBTarget=-26,snrs=[15],noiseNum=10,totalSamples=1000):
    sampleN=0
    idx=0
    while sampleN<totalSamples:
        noises=random.sample(noisefiles,noiseNum)
        sounds=soundfiles[sampleN:sampleN+noiseNum]
        sampleN+=noiseNum
        for noisefile,soundfile in zip(noises,sounds):
            snr=random.choice(snrs)
            mixedsound=mixsoundnoisepair(soundfile,noisefile,wnd,soundDBTarget,snr)
            mixedsound.export(outputDir+str(idx)+'.wav', format="wav")
            idx+=1

def generateNormalizedNoiseDir(dataDir,noiseFiles,outputNoiseDir,wnd,noiseDBTargets):
    if not os.path.exists(dataDir+outputNoiseDir):
        os.system('mkdir {}{}'.format(dataDir,outputNoiseDir))
    idx=0
    for noisefile in noiseFiles:
        noiseDBTarget=random.choice(noiseDBTargets)
        n=normalizeaudio(noisefile,wnd,noiseDBTarget)
        n.export(dataDir+outputNoiseDir+str(idx)+'.wav',format='wav')
        idx+=1
    
    

def generateData(dataDir,voiceTrainDir,voiceTestDir,noiseTrains,noiseTests,\
                 outputTrainDir,outputTestDir,\
                 outputNoiseTrainDir,outputNoiseTestDir,\
                 wnd,soundDBTarget,snrs):
    if not os.path.exists(dataDir+outputTestDir):
        os.system('mkdir {}{}'.format(dataDir,outputTestDir))
    if not os.path.exists(dataDir+outputTrainDir):
        os.system('mkdir {}{}'.format(dataDir,outputTrainDir))
        
    voiceTrainFiles,voiceTestFiles=[dataDir+voiceTrainDir+f for f in os.listdir(dataDir+voiceTrainDir) if '.wav' in f],[dataDir+voiceTestDir+f for f in os.listdir(dataDir+voiceTestDir) if '.wav' in f]
    noiseTrainFiles,noiseTestFiles=[],[]
    for directory in noiseTrains:
        noiseTrainFiles+=[dataDir+directory+f for f in os.listdir(dataDir+directory) if '.wav' in f]
    for directory in noiseTests:
        noiseTestFiles+=[dataDir+directory+f for f in os.listdir(dataDir+directory) if '.wav' in f]
    
    #shuffle
    shuffle(voiceTestFiles)
    shuffle(voiceTrainFiles)
    shuffle(noiseTestFiles)
    shuffle(noiseTrainFiles)
    
    mixnoises_sounds(voiceTrainFiles,noiseTrainFiles,dataDir+outputTrainDir,wnd,soundDBTarget,snrs,noiseNum=20,totalSamples=2000)
    mixnoises_sounds(voiceTestFiles,noiseTestFiles,dataDir+outputTestDir,wnd,soundDBTarget,snrs,noiseNum=20,totalSamples=500)
    
    generateNormalizedNoiseDir(dataDir,noiseTrainFiles,outputNoiseTrainDir,wnd,noiseDBTargets=[soundDBTarget])
    generateNormalizedNoiseDir(dataDir,noiseTestFiles,outputNoiseTestDir,wnd,noiseDBTargets=[soundDBTarget])
    
    
         

if __name__ == '__main__':
      
    splitTrainTest('./freesound_noise/crowd/','./processed/crowdTrain/','./processed/crowdTest/')
    splitTrainTest('./freesound_noise/keyboard/','./processed/keyboardTrain/','./processed/keyboardTest/')
    splitTrainTest('./freesound_noise/lawnmower/','./processed/lawnmowerTrain/','./processed/lawnmowerTest/')
    splitTrainTest('./freesound_noise/dog/','./processed/dogTrain/','./processed/dogTest/')
    splitTrainTest('./freesound_noise/mouseclick/','./processed/mouseclickTrain/','./processed/mouseclickTest/')
    splitTrainTest('./freesound_noise/passingcar/','./processed/passingcarTrain/','./processed/passingcarTest/')
    splitTrainTest('./freesound_noise/caralarm/','./processed/caralarmTrain/','./processed/caralarmTest/')
    splitTrainTest('./freesound_noise/plane/','./processed/planeTrain/','./processed/planeTest/')
    cleanwavPickTrainTest('/Users/dengjiachuan/Desktop/audioData/AURORA4/aurora4/train_si84_clean/',\
                     './processed/cleanTrain/',\
                     './processed/cleanTest/',
                     2000,500)
    generateData('./processed/',\
            'cleanTrain/',\
            'cleanTest/',\
            ['dogTrain/','keyboardTrain/','lawnmowerTrain/','mouseclickTrain/','caralarmTrain/','planeTrain/'],\
            ['dogTest/','keyboardTest/','lawnmowerTest/','mouseclickTest/','caralarmTest/','planeTest/'],\
            'trainNoisyData15dB/','testNoisyData15dB/',\
             'trainNoise15dB/','testNoise15dB/',\
            wnd=50,soundDBTarget=-26,snrs=[15,10,5])

    files=[f for f in os.listdir('/Users/dengjiachuan/Desktop/realmeet3/') if '.wav' in f]
    samplefiles=random.sample(files,200)

    for f in samplefiles:
        os.system('cp {}{} {}'.format('/Users/dengjiachuan/Desktop/realmeet3/',f,'/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/realtest/testNoisyData15dB/'))

    
    files=[f for f in os.listdir('/Users/dengjiachuan/Desktop/realmeet2/') if '.wav' in f]
    samplefiles=random.sample(files,150)

    for f in samplefiles:
        os.system('cp {}{} {}'.format('/Users/dengjiachuan/Desktop/realmeet2/',f,'/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/realtest/testNoisyData15dB/'))


    files=[f for f in os.listdir('/Users/dengjiachuan/Desktop/realmeet1/') if '.wav' in f]
    samplefiles=random.sample(files,200)

    for f in samplefiles:
        os.system('cp {}{} {}'.format('/Users/dengjiachuan/Desktop/realmeet1/',f,'/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/realtest/testNoisyData15dB/'))

    
    origdir='/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/realtest/testNoisyData15dB/'
    noiseFiles=[origdir+f for f in os.listdir(origdir) if '.wav' in f]

    generateNormalizedNoiseDir('/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/realtest/',\
                               noiseFiles,outputNoiseDir='testNoisyData15dBNorm/',wnd=50,noiseDBTargets=[-26])


    files=[f for f in os.listdir('/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/selfbuildDataTest15dB/testNoisyData15dB/') if '.wav' in f]
    samplefiles=random.sample(files,150)

    for f in samplefiles:
        fn=f.split('.')[0]
        fn=fn+"self.wav"
        os.system('cp {}{} {}{}'.format('/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/selfbuildDataTest15dB/testNoisyData15dB/',f,'/Users/dengjiachuan/Desktop/zoom_intern_server/noise_recog/data/realtest/testNoisyData15dBNorm/',fn))



    