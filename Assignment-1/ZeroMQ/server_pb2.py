# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: server.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cserver.proto\x12\x07pubsubs\"\xa3\x01\n\rServerMessage\x12/\n\rclientDetails\x18\x01 \x01(\x0b\x32\x16.pubsubs.ClientDetailsH\x00\x12*\n\x0epublishArticle\x18\x02 \x01(\x0b\x32\x10.pubsubs.ArticleH\x00\x12-\n\ngetArticle\x18\x03 \x01(\x0b\x32\x17.pubsubs.RequestMessageH\x00\x42\x06\n\x04Type\"A\n\rClientDetails\x12\x13\n\x0b\x63lient_uuid\x18\x01 \x01(\t\x12\x0c\n\x04join\x18\x02 \x01(\x08\x12\r\n\x05leave\x18\x03 \x01(\x08\"/\n\x15StatusOfClientRequest\x12\x16\n\x0erequest_status\x18\x01 \x01(\x08\"\xb1\x01\n\x07\x41rticle\x12\x10\n\x06SPORTS\x18\x01 \x01(\x08H\x00\x12\x11\n\x07\x46\x41SHION\x18\x02 \x01(\x08H\x00\x12\x12\n\x08POLITICS\x18\x03 \x01(\x08H\x00\x12\x0e\n\x06\x61uthor\x18\x04 \x01(\t\x12\x0b\n\x03\x64\x61y\x18\x05 \x01(\x05\x12\r\n\x05month\x18\x06 \x01(\x05\x12\x0c\n\x04year\x18\x07 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x08 \x01(\t\x12\x13\n\x0b\x63lient_uuid\x18\t \x01(\tB\r\n\x0b\x41rticleTags\"\xb3\x01\n\x0eRequestMessage\x12\x11\n\x07\x61llTags\x18\x01 \x01(\x08H\x00\x12\x10\n\x06SPORTS\x18\x02 \x01(\x08H\x00\x12\x11\n\x07\x46\x41SHION\x18\x03 \x01(\x08H\x00\x12\x12\n\x08POLITICS\x18\x04 \x01(\x08H\x00\x12\x0e\n\x06\x61uthor\x18\x05 \x01(\t\x12\x0b\n\x03\x64\x61y\x18\x06 \x01(\x05\x12\r\n\x05month\x18\x07 \x01(\x05\x12\x0c\n\x04year\x18\x08 \x01(\x05\x12\x13\n\x0b\x63lient_uuid\x18\t \x01(\tB\x06\n\x04Tags\"A\n\x0b\x41rticleList\x12\"\n\x08\x61rticles\x18\x01 \x03(\x0b\x32\x10.pubsubs.Article\x12\x0e\n\x06status\x18\x02 \x01(\x08\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _SERVERMESSAGE._serialized_start=26
  _SERVERMESSAGE._serialized_end=189
  _CLIENTDETAILS._serialized_start=191
  _CLIENTDETAILS._serialized_end=256
  _STATUSOFCLIENTREQUEST._serialized_start=258
  _STATUSOFCLIENTREQUEST._serialized_end=305
  _ARTICLE._serialized_start=308
  _ARTICLE._serialized_end=485
  _REQUESTMESSAGE._serialized_start=488
  _REQUESTMESSAGE._serialized_end=667
  _ARTICLELIST._serialized_start=669
  _ARTICLELIST._serialized_end=734
# @@protoc_insertion_point(module_scope)
