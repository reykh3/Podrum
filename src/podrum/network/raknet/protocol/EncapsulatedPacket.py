"""
*  ____           _
* |  _ \ ___   __| |_ __ _   _ _ __ ___
* | |_) / _ \ / _` | '__| | | | '_ ` _ \
* |  __/ (_) | (_| | |  | |_| | | | | | |
* |_|   \___/ \__,_|_|   \__,_|_| |_| |_|
*
* Licensed under the Apache License, Version 2.0 (the "License")
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
"""

from binutilspy.BinaryStream import BinaryStream
from podrum.network.raknet.Reliability import Reliability

class EncapsulatedPacket:
    buffer = None
    messageIndex = None
    sequenceIndex = None
    orderIndex = None
    orderChannel = None
    split = None
    splitCount = None
    splitIndex = None
    splitId = None
    
    @staticmethod
    def fromBinary(stream):
        packet = EncapsulatedPacket()
        header = stream.getByte()
        packet.reliability = (header & 224) >> 5
        packet.split = (header & 0x10) > 0
        length = stream.getShort() >> 3
        if length == 0:
            raise Exception("Got an empty encapsulated packet")       
        if Reliability.isReliable(packet.reliability):
            packet.messageIndex = stream.getLTriad()
        if Reliability.isSequenced(packet.reliability):
            packet.sequenceIndex = stream.getLTriad()
        if Reliability.isSequencedOrOrdered(packet.reliability):
            packet.orderIndex = stream.getLTriad()
            packet.orderChannel = stream.getByte()
        if packet.split:
            packet.splitCount = stream.getInt()
            packet.splitId = stream.getShort()
            packet.splitIndex = stream.getInt()
        packet.buffer = stream.buffer[stream.offset:]
        stream.offset += length
        return packet

    def toBinary(self):
        stream = BinaryStream()
        header = self.reliability << 5
        if self.split:
            header |= 0x10
        stream.putByte(header)
        stream.putShort(len(self.buffer) << 3)
        if Reliability.isReliable(self.reliability):
            stream.putLTriad(self.messageIndex)
        if Reliability.isSequenced(self.reliability):
            stream.putLTriad(self.sequenceIndex)
        if Reliability.isSequencedOrOrdered(self.reliability):
            stream.putLTriad(self.orderIndex)
            stream.putByte(self.orderChannel)
        if packet.split:
            stream.putInt(self.splitCount)
            stream.putShort(self.splitId)
            stream.putInt(self.splitIndex)
        stream.put(self.buffer)
        return stream
    
    def getTotalLength(self):
        length = 3
        length += len(self.buffer)
        length += 3 if self.messageIndex else 0
        length += 4 if self.orderIndex else 0
        length += 10 if self.split else 0
        return length
