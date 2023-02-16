import wave


def main():
    # for nNumChannel in range(1, 4):
    #     # convert to wav???
    #     strFilenameOut = "./out.raw"
    #     strFilenameOutChan = strFilenameOut.replace(".raw", "_%d.raw" % nNumChannel)
    #     strFilenameOutChanWav = strFilenameOutChan.replace(".raw", ".wav")
    #     fileNameFinal = strFilenameOutChanWav
    #     with open(strFilenameOutChan, "rb") as inp_f:
    #         data = inp_f.read()
    #         out_f = wave.open(strFilenameOutChanWav, "wb")
    #         out_f.setnchannels(1)
    #         out_f.setsampwidth(2)  # number of bytes
    #         out_f.setframerate(44100)
    #         out_f.writeframesraw(data)
    #         out_f.close()
    # convert to wav???
    strFilenameOut = "./out.raw"
    strFilenameOutChanWav = strFilenameOut.replace(".raw", ".wav")
    fileNameFinal = strFilenameOutChanWav
    with open(strFilenameOut, "rb") as inp_f:
        data = inp_f.read()
        out_f = wave.open(strFilenameOutChanWav, "wb")
        out_f.setnchannels(1)
        out_f.setsampwidth(2)  # number of bytes
        out_f.setframerate(44100)
        out_f.writeframesraw(data)
        out_f.close()


if __name__ == "__main__":
    main()
