import cv2
import threading
import queue

lock = threading.Lock()


def addToQue(QueSemaphor, que, frame):
    QueSemaphor.acquire()
    lock.acquire()
    que.put(frame)
    lock.release()


def getFromQue(QueSemaphor, que):
    QueSemaphor.release()
    lock.acquire()
    frame = que.get()
    lock.release()
    return frame


def isEmpty(que):
    lock.acquire()
    queStatus = que.empty()
    lock.release()
    return queStatus


def convertToGray(producer, customer, max, producerSemFunc, consumerSemFunc):
    count = 0
    while True:
        if isEmpty(producerQue):
            continue
        Frame = getFromQue(producerSemFunc, producer)
        if count == max:
            break
        print(f'converting frame {count} to grayscale')
        grayScaleFrame = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY)
        addToQue(consumerSemFunc, customer, grayScaleFrame)
        count += 1
    print("conversion complete")


def extractFrames(producer, fileName, max, producerSemFunc):
    count = 0
    vidcap = cv2.VideoCapture(fileName)
    success, image = vidcap.read()
    while success and count < max:
        success, jpgImage = cv2.imencode('.jpg', image)
        addToQue(producerSemFunc, producer, image)
        success, image = vidcap.read()
        print(f'reading frame {count} {success}')
        count += 1
    print('Frame extraction complete')


def displayFrames(consumer, maxFrames, consumerSemFunc):
    count = 0
    while True:
        if isEmpty(consumer):
            continue
        if count == maxFrames:
            break
        displayFrame = getFromQue(consumerSemFunc, consumer)
        print(f'displaying frame {count}')
        cv2.imshow('Video', displayFrame)
        if cv2.waitKey(42) and 0xFF == ord('q'):  # wait 42ms
            break
        count += 1
    print("display finished")
    cv2.destroyAllWindows()


producerQue = queue.Queue()
producerSem = threading.Semaphore(10)
consumerQue = queue.Queue()
consumerSem = threading.Semaphore(10)
fileName = "clip.mp4"
maxCount = 9999
extractThread = threading.Thread(target=extractFrames, args=(producerQue, fileName, maxCount, producerSem))
convertThread = threading.Thread(target=convertToGray, args=(producerQue, consumerQue, maxCount, producerSem, consumerSem))
displayThread = threading.Thread(target=displayFrames, args=(consumerQue, maxCount,consumerSem))
extractThread.start()
convertThread.start()
displayThread.start()
