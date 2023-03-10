# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: command.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rcommand.proto\x12\tcommander\"l\n\tQueryInfo\x12\x0b\n\x03qid\x18\x01 \x01(\r\x12\n\n\x02\x61x\x18\x02 \x01(\x02\x12\n\n\x02\x61y\x18\x03 \x01(\x02\x12\n\n\x02\x62x\x18\x04 \x01(\x02\x12\n\n\x02\x62y\x18\x05 \x01(\x02\x12\x0b\n\x03max\x18\x06 \x01(\r\x12\x15\n\rtrackableOnly\x18\x07 \x01(\x08\"7\n\x06NEvent\x12\x0c\n\x04ints\x18\x02 \x03(\x05\x12\x0e\n\x06\x66loats\x18\x03 \x03(\x02\x12\x0f\n\x07strings\x18\x04 \x03(\t\"\x8d\x03\n\nNStageInfo\x12\n\n\x02sn\x18\x01 \x01(\r\x12\x12\n\nbackground\x18\x02 \x01(\t\x12\x10\n\x08gravityX\x18\x03 \x01(\x02\x12\x10\n\x08gravityY\x18\x04 \x01(\x02\x12\r\n\x05width\x18\x05 \x01(\x02\x12\x0e\n\x06height\x18\x06 \x01(\x02\x12\r\n\x05\x64\x65\x62ug\x18\x07 \x01(\x08\x12=\n\x14joystickDirectionals\x18\x08 \x01(\x0e\x32\x1f.commander.JoystickDirectionals\x12\x19\n\x11joystickPrecision\x18\t \x01(\r\x12\'\n\x07\x62utton1\x18\n \x01(\x0e\x32\x16.commander.TouchMotion\x12\'\n\x07\x62utton2\x18\x0b \x01(\x0e\x32\x16.commander.TouchMotion\x12#\n\x03tap\x18\x0c \x01(\x0e\x32\x16.commander.TouchMotion\x12\x1a\n\x12tapMinMoveDistance\x18\r \x01(\x02\x12 \n\x18\x64istanceTrackingInternal\x18\x0e \x01(\x02\"O\n\x03\x43md\x12\n\n\x02sn\x18\x01 \x01(\r\x12\x0c\n\x04ints\x18\x02 \x03(\x05\x12\x0e\n\x06\x66loats\x18\x03 \x03(\x02\x12\x0f\n\x07strings\x18\x04 \x03(\t\x12\r\n\x05\x62ytes\x18\x05 \x03(\x0c\"\x9e\x01\n\x07NObject\x12\n\n\x02sn\x18\x01 \x01(\r\x12\n\n\x02id\x18\x02 \x01(\x05\x12#\n\x04\x62ody\x18\x03 \x01(\x0b\x32\x10.commander.NBodyH\x00\x88\x01\x01\x12\'\n\x06visual\x18\x04 \x01(\x0b\x32\x12.commander.NVisualH\x01\x88\x01\x01\x12\x0b\n\x03tid\x18\x05 \x01(\r\x12\x0c\n\x04info\x18\x06 \x01(\tB\x07\n\x05_bodyB\t\n\x07_visual\"\xda\x01\n\x07NVisual\x12%\n\x07\x63urrent\x18\x01 \x01(\x0e\x32\x14.commander.NClipType\x12\x10\n\x08priority\x18\x02 \x01(\r\x12\t\n\x01x\x18\x03 \x01(\x02\x12\t\n\x01y\x18\x04 \x01(\x02\x12\r\n\x05width\x18\x05 \x01(\x02\x12\x0e\n\x06height\x18\x06 \x01(\x02\x12\x0e\n\x06scaleX\x18\x07 \x01(\x02\x12\x0e\n\x06scaleY\x18\x08 \x01(\x02\x12\x0f\n\x07\x61nchorX\x18\t \x01(\x02\x12\x0f\n\x07\x61nchorY\x18\n \x01(\x02\x12\x1f\n\x05\x63lips\x18\x0b \x03(\x0b\x32\x10.commander.NClip\"\xa1\x01\n\x05NClip\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\t\n\x01x\x18\x02 \x01(\x02\x12\t\n\x01y\x18\x03 \x01(\x02\x12\r\n\x05width\x18\x04 \x01(\x02\x12\x0e\n\x06height\x18\x05 \x01(\x02\x12\x0f\n\x07indices\x18\x06 \x03(\r\x12\x10\n\x08stepTime\x18\x07 \x01(\x02\x12\"\n\x04type\x18\x08 \x01(\x0e\x32\x14.commander.NClipType\x12\x0e\n\x06repeat\x18\t \x01(\x08\"\xee\x02\n\x05NBody\x12!\n\x04type\x18\x01 \x01(\x0e\x32\x13.commander.BodyType\x12#\n\x05shape\x18\x02 \x01(\x0e\x32\x14.commander.BodyShape\x12\t\n\x01x\x18\x03 \x01(\x02\x12\t\n\x01y\x18\x04 \x01(\x02\x12\r\n\x05width\x18\x05 \x01(\x02\x12\x0e\n\x06height\x18\x06 \x01(\x02\x12\x13\n\x0brestitution\x18\x07 \x01(\x02\x12\x10\n\x08\x66riction\x18\x08 \x01(\x02\x12\x0f\n\x07\x64\x65nsity\x18\t \x01(\x02\x12\r\n\x05\x61ngle\x18\n \x01(\x02\x12\x10\n\x08isSensor\x18\x0b \x01(\x08\x12\x14\n\x0c\x63\x61tegoryBits\x18\x0c \x01(\r\x12\x10\n\x08maskBits\x18\r \x01(\r\x12\x15\n\rfixedRotation\x18\x0e \x01(\x08\x12\x11\n\ttrackable\x18\x0f \x01(\x08\x12\x15\n\rcontactReport\x18\x10 \x01(\x08\x12\x0e\n\x06\x66loats\x18\x11 \x03(\x02\x12\x16\n\x0epassableBottom\x18\x12 \x01(\x08*\xc2\x01\n\x04Head\x12\x07\n\x03\x63md\x10\x00\x12\x0b\n\x05stage\x10\x80\xfe\x03\x12\x0b\n\x05query\x10\x84\xfe\x03\x12\x0c\n\x06object\x10\x86\xfe\x03\x12\r\n\x07\x63ontact\x10\xf0\xe1\x03\x12\x0b\n\x05\x65vent\x10\xf1\xe1\x03\x12\t\n\x03key\x10\xf2\xe1\x03\x12\t\n\x03\x61\x63k\x10\xf3\xe1\x03\x12\x11\n\x0b\x64irectional\x10\xf4\xe1\x03\x12\x0c\n\x06\x62utton\x10\xf5\xe1\x03\x12\t\n\x03tap\x10\xf6\xe1\x03\x12\x11\n\x0bqueryresult\x10\xf7\xe1\x03\x12\x0b\n\x05\x65rror\x10\xf8\xe1\x03\x12\x0b\n\x05relay\x10\xf9\xe1\x03*V\n\tBodyShape\x12\r\n\trectangle\x10\x00\x12\t\n\x05\x61\x63tor\x10\x01\x12\n\n\x06\x63ircle\x10\x02\x12\x0c\n\x08triangle\x10\x03\x12\x08\n\x04\x65\x64ge\x10\x04\x12\x0b\n\x07polygon\x10\x05*>\n\x08\x42odyType\x12\x0e\n\nstaticBody\x10\x00\x12\x11\n\rkinematicBody\x10\x01\x12\x0f\n\x0b\x64ynamicBody\x10\x02*\xac\x01\n\x17JoystickMoveDirectional\x12\x0b\n\x07MOVE_UP\x10\x00\x12\x10\n\x0cMOVE_UP_LEFT\x10\x01\x12\x11\n\rMOVE_UP_RIGHT\x10\x02\x12\x0e\n\nMOVE_RIGHT\x10\x03\x12\r\n\tMOVE_DOWN\x10\x04\x12\x13\n\x0fMOVE_DOWN_RIGHT\x10\x05\x12\x12\n\x0eMOVE_DOWN_LEFT\x10\x06\x12\r\n\tMOVE_LEFT\x10\x07\x12\x08\n\x04IDLE\x10\x08*I\n\x0bTouchMotion\x12\x08\n\x04NONE\x10\x00\x12\x08\n\x04\x44OWN\x10\x01\x12\x08\n\x04MOVE\x10\x02\x12\x06\n\x02UP\x10\x04\x12\x0b\n\x07\x44OWN_UP\x10\x05\x12\x07\n\x03\x41LL\x10\x07*S\n\x0cTouchInputId\x12\x11\n\rjoystickInput\x10\x00\x12\x10\n\x0c\x62utton1Input\x10\x01\x12\x10\n\x0c\x62utton2Input\x10\x02\x12\x0c\n\x08tapInput\x10\x03*G\n\x14JoystickDirectionals\x12\x08\n\x04none\x10\x00\x12\x07\n\x03\x61ll\x10\x01\x12\x0e\n\nhorizontal\x10\x02\x12\x0c\n\x08vertical\x10\x03*\xaa\x02\n\tNClipType\x12\x08\n\x04idle\x10\x00\x12\x07\n\x03run\x10\x01\x12\x08\n\x04jump\x10\x02\x12\x07\n\x03hit\x10\x03\x12\x08\n\x04\x66\x61ll\x10\x04\x12\x0c\n\x08wallJump\x10\x05\x12\x0e\n\ndoubleJump\x10\x06\x12\x0b\n\x07hitSide\x10\x07\x12\n\n\x06hitTop\x10\x08\x12\x07\n\x03off\x10\t\x12\x06\n\x02on\x10\n\x12\t\n\x05\x62link\x10\x0b\x12\x0b\n\x07hitLeft\x10\x0c\x12\x0c\n\x08hitRight\x10\r\x12\r\n\thitBottom\x10\x0e\x12\x0c\n\x08noChange\x10\x0f\x12\t\n\x05tiles\x10\x10\x12\x07\n\x03svg\x10\x11\x12\x06\n\x02t0\x10\x12\x12\x06\n\x02t1\x10\x13\x12\x06\n\x02t2\x10\x14\x12\x06\n\x02t3\x10\x15\x12\x06\n\x02t4\x10\x16\x12\x06\n\x02t5\x10\x17\x12\x06\n\x02t6\x10\x18\x12\x06\n\x02t7\x10\x19\x12\x06\n\x02t8\x10\x1a\x12\x06\n\x02t9\x10\x1b\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'command_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _HEAD._serialized_start=1592
  _HEAD._serialized_end=1786
  _BODYSHAPE._serialized_start=1788
  _BODYSHAPE._serialized_end=1874
  _BODYTYPE._serialized_start=1876
  _BODYTYPE._serialized_end=1938
  _JOYSTICKMOVEDIRECTIONAL._serialized_start=1941
  _JOYSTICKMOVEDIRECTIONAL._serialized_end=2113
  _TOUCHMOTION._serialized_start=2115
  _TOUCHMOTION._serialized_end=2188
  _TOUCHINPUTID._serialized_start=2190
  _TOUCHINPUTID._serialized_end=2273
  _JOYSTICKDIRECTIONALS._serialized_start=2275
  _JOYSTICKDIRECTIONALS._serialized_end=2346
  _NCLIPTYPE._serialized_start=2349
  _NCLIPTYPE._serialized_end=2647
  _QUERYINFO._serialized_start=28
  _QUERYINFO._serialized_end=136
  _NEVENT._serialized_start=138
  _NEVENT._serialized_end=193
  _NSTAGEINFO._serialized_start=196
  _NSTAGEINFO._serialized_end=593
  _CMD._serialized_start=595
  _CMD._serialized_end=674
  _NOBJECT._serialized_start=677
  _NOBJECT._serialized_end=835
  _NVISUAL._serialized_start=838
  _NVISUAL._serialized_end=1056
  _NCLIP._serialized_start=1059
  _NCLIP._serialized_end=1220
  _NBODY._serialized_start=1223
  _NBODY._serialized_end=1589
# @@protoc_insertion_point(module_scope)
