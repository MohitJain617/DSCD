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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cserver.proto\x12\x06pubsub\"\x07\n\x05\x45mpty\"$\n\rClientDetails\x12\x13\n\x0b\x63lient_uuid\x18\x01 \x01(\t\"/\n\x15StatusOfClientRequest\x12\x16\n\x0erequest_status\x18\x01 \x01(\x08\"+\n\rServerDetails\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04\x61\x64\x64r\x18\x02 \x01(\t\"7\n\nServerList\x12)\n\nserverlist\x18\x01 \x03(\x0b\x32\x15.pubsub.ServerDetails\"\xc3\x01\n\x07\x41rticle\x12\x10\n\x06SPORTS\x18\x01 \x01(\x08H\x00\x12\x11\n\x07\x46\x41SHION\x18\x02 \x01(\x08H\x00\x12\x12\n\x08POLITICS\x18\x03 \x01(\x08H\x00\x12\x0e\n\x06\x61uthor\x18\x04 \x01(\t\x12\x0b\n\x03\x64\x61y\x18\x05 \x01(\x05\x12\r\n\x05month\x18\x06 \x01(\x05\x12\x0c\n\x04year\x18\x07 \x01(\x05\x12\x0f\n\x07\x63ontent\x18\x08 \x01(\t\x12%\n\x06\x63lient\x18\t \x01(\x0b\x32\x15.pubsub.ClientDetailsB\r\n\x0b\x41rticleTags\"\xc5\x01\n\x0eRequestMessage\x12\x11\n\x07\x61llTags\x18\x01 \x01(\x08H\x00\x12\x10\n\x06SPORTS\x18\x02 \x01(\x08H\x00\x12\x11\n\x07\x46\x41SHION\x18\x03 \x01(\x08H\x00\x12\x12\n\x08POLITICS\x18\x04 \x01(\x08H\x00\x12\x0e\n\x06\x61uthor\x18\x05 \x01(\t\x12\x0b\n\x03\x64\x61y\x18\x06 \x01(\x05\x12\r\n\x05month\x18\x07 \x01(\x05\x12\x0c\n\x04year\x18\x08 \x01(\x05\x12%\n\x06\x63lient\x18\t \x01(\x0b\x32\x15.pubsub.ClientDetailsB\x06\n\x04Tags\"0\n\x0b\x41rticleList\x12!\n\x08\x61rticles\x18\x01 \x03(\x0b\x32\x0f.pubsub.Article2\xcd\x02\n\x06Server\x12\x34\n\rGetServerList\x12\r.pubsub.Empty\x1a\x12.pubsub.ServerList\"\x00\x12\x44\n\nJoinServer\x12\x15.pubsub.ClientDetails\x1a\x1d.pubsub.StatusOfClientRequest\"\x00\x12\x45\n\x0bLeaveServer\x12\x15.pubsub.ClientDetails\x1a\x1d.pubsub.StatusOfClientRequest\"\x00\x12<\n\x0bGetArticles\x12\x16.pubsub.RequestMessage\x1a\x13.pubsub.ArticleList\"\x00\x12\x42\n\x0ePublishArticle\x12\x0f.pubsub.Article\x1a\x1d.pubsub.StatusOfClientRequest\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EMPTY._serialized_start=24
  _EMPTY._serialized_end=31
  _CLIENTDETAILS._serialized_start=33
  _CLIENTDETAILS._serialized_end=69
  _STATUSOFCLIENTREQUEST._serialized_start=71
  _STATUSOFCLIENTREQUEST._serialized_end=118
  _SERVERDETAILS._serialized_start=120
  _SERVERDETAILS._serialized_end=163
  _SERVERLIST._serialized_start=165
  _SERVERLIST._serialized_end=220
  _ARTICLE._serialized_start=223
  _ARTICLE._serialized_end=418
  _REQUESTMESSAGE._serialized_start=421
  _REQUESTMESSAGE._serialized_end=618
  _ARTICLELIST._serialized_start=620
  _ARTICLELIST._serialized_end=668
  _SERVER._serialized_start=671
  _SERVER._serialized_end=1004
# @@protoc_insertion_point(module_scope)
