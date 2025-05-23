"""Event fixtures."""

FIRST_MESSAGE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n</tt:MetadataStream>\n'

AUDIO_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:AudioSource/tnsaxis:TriggerLevel</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://1c8ae81b-3b00-46cf-bf76-79cc3fa533dc/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-02-06T18:58:50.922426Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="channel" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="triggered" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

DAYNIGHT_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:VideoSource/tnsaxis:DayNightVision</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://1c8ae81b-3b00-46cf-bf76-79cc3fa533dc/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-02-06T18:58:51.007104Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="VideoSourceConfigurationToken" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="day" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

FENCE_GUARD_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/FenceGuard/Camera1Profile1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-09-04T20:08:34.701060Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

GLOBAL_SCENE_CHANGE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:VideoSource/GlobalSceneChange/ImagingService</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-09-05T04:45:30.199233Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="Source" Value="0"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="State" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

LIGHT_STATUS_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:Device/tnsaxis:Light/Status</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-09-05T04:25:51.692744Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="id" Value="0"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="state" Value="OFF"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

LIGHT_STATUS_CHANGED_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:LightControl/tnsaxis:LightStatusChanged/Status</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-09-04T21:00:34.890148Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="state" Value="ON"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

LOITERING_GUARD_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/LoiteringGuard/Camera1Profile1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-09-04T20:57:25.764426Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

MOTION_GUARD_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/MotionGuard/Camera1ProfileANY</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-09-04T21:01:36.676377Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

OBJECT_ANALYTICS_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://4b2daa4c-507e-482c-8ae0-2068b1c1d875/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-09-04T21:44:04.840805Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
OBJECT_ANALYTICS_ANY_CHANGE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event>\n<wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics"\nxmlns:tnsaxis="http://www.axis.com/2009/event/topics"\nxmlns:wsnt="http://docs.oasis-open.org/wsn/b-2"\nxmlns:wsa5="http://www.w3.org/2005/08/addressing">\n<wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1</wsnt:Topic>\n<wsnt:ProducerReference>\n<wsa5:Address>uri://cfbf96f2-9dc7-437f-aa12-155aacbb0b8f/ProducerReference</wsa5:Address>\n</wsnt:ProducerReference>\n<wsnt:Message>\n<tt:Message UtcTime="2024-10-07T21:09:26.046851Z" PropertyOperation="Changed">\n<tt:Source></tt:Source>\n<tt:Key></tt:Key>\n<tt:Data>\n<tt:SimpleItem Name="classTypes" Value="human"/>\n<tt:SimpleItem Name="active" Value="1"/>\n<tt:SimpleItem Name="objectId" Value="234232"/>\n</tt:Data>\n</tt:Message>\n</wsnt:Message>\n</wsnt:NotificationMessage>\n</tt:Event>\n</tt:MetadataStream>\n'

PIR_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:Device/tnsaxis:Sensor/PIR</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-12T23:48:26.371215Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="sensor" Value="0"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="state" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PIR_CHANGE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:Device/tnsaxis:Sensor/PIR</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-12T23:48:28.425164Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="sensor" Value="0"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="state" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

PORT_0_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:Device/tnsaxis:IO/Port</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://4205c5dc-6132-44ad-9aa5-52172e062d2b/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-01-15T07:50:45.206264Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="port" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="state" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

PORT_ANY_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:Device/tnsaxis:IO/Port</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://4205c5dc-6132-44ad-9aa5-52172e062d2b/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-04-19T09:46:27.878886Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="port" Value="-1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="state" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

PTZ_MOVE_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:Move/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T19:37:19.764701Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="PTZConfigurationToken" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="is_moving" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_MOVE_START = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:Move/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:04:53.005004Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PTZConfigurationToken" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="is_moving" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_MOVE_END = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:Move/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:04:54.439178Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PTZConfigurationToken" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="is_moving" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

PTZ_PRESET_INIT_1 = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:21:48.346022Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="PresetToken" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_PRESET_INIT_2 = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:04:52.991661Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="PresetToken" Value="2"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_PRESET_INIT_3 = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T19:36:53.551212Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="PresetToken" Value="3"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

PTZ_PRESET_AT_1_TRUE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:22:29.579385Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PresetToken" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_PRESET_AT_1_FALSE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:22:13.110514Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PresetToken" Value="1"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_PRESET_AT_2_TRUE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:22:17.353366Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PresetToken" Value="2"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_PRESET_AT_2_FALSE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:22:19.566678Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PresetToken" Value="2"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_PRESET_AT_3_TRUE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:22:23.346288Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PresetToken" Value="3"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
PTZ_PRESET_AT_3_FALSE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:PTZController/tnsaxis:PTZPresets/Channel_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://bf32a3b9-e5e7-4d57-a48d-1b5be9ae7b16/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-11-03T20:22:26.584156Z" PropertyOperation="Changed"><tt:Source><tt:SimpleItem Name="PresetToken" Value="3"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="on_preset" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

RELAY_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:Device/Trigger/Relay</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://4205c5dc-6132-44ad-9aa5-52172e062d2b/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-04-22T20:13:20.192659Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="RelayToken" Value="3"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="LogicalState" Value="inactive"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

VMD3_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-04-17T09:30:44.352231Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="areaid" Value="0"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

VMD4_ANY_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-12T23:32:17.591254Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
VMD4_ANY_CHANGE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/VMD/Camera1ProfileANY</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-13T00:03:30.256687Z" PropertyOperation="Changed"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

VMD4_C1P1_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-12T23:32:17.591253Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
VMD4_C1P1_CHANGE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile1</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-13T00:03:30.256685Z" PropertyOperation="Changed"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

VMD4_C1P2_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile2</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-12T22:48:39.713432Z" PropertyOperation="Initialized"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'
VMD4_C1P2_CHANGE = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile2</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://94fbe18e-0af8-40d2-8539-67b6ea550c6e/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2019-03-13T00:04:56.175457Z" PropertyOperation="Changed"><tt:Source></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="active" Value="1"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

# Event with source in a list
RULE_ENGINE_REGION_DETECTOR_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tns1:RuleEngine/MotionRegionDetector/Motion</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2021-01-06T17:46:45.115382Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="VideoSource" Value="0"/><tt:SimpleItem Name="RuleName" Value="Profile 1V"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="State" Value="0"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'

# Event with data in a list
STORAGE_ALERT_INIT = b'<?xml version="1.0" encoding="UTF-8"?>\n<tt:MetadataStream xmlns:tt="http://www.onvif.org/ver10/schema">\n<tt:Event><wsnt:NotificationMessage xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:wsa5="http://www.w3.org/2005/08/addressing"><wsnt:Topic Dialect="http://docs.oasis-open.org/wsn/t-1/TopicExpression/Simple">tnsaxis:Storage/Alert</wsnt:Topic><wsnt:ProducerReference><wsa5:Address>uri://755cc9bb-cf3a-410b-bd1b-0ec97c6d6256/ProducerReference</wsa5:Address></wsnt:ProducerReference><wsnt:Message><tt:Message UtcTime="2020-06-02T20:35:42.477710Z" PropertyOperation="Initialized"><tt:Source><tt:SimpleItem Name="disk_id" Value="NetworkShare"/></tt:Source><tt:Key></tt:Key><tt:Data><tt:SimpleItem Name="overall_health" Value="-3"/><tt:SimpleItem Name="alert" Value="0"/><tt:SimpleItem Name="wear" Value="-3"/><tt:SimpleItem Name="temperature" Value="-3"/></tt:Data></tt:Message></wsnt:Message></wsnt:NotificationMessage></tt:Event></tt:MetadataStream>\n'


# Event instances

EVENT_INSTANCES = """<?xml version="1.0" encoding="UTF-8"?>\n
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:c14n="http://www.w3.org/2001/10/xml-exc-c14n#" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsa5="http://www.w3.org/2005/08/addressing" xmlns:xmime="http://tempuri.org/xmime.xsd" xmlns:xop="http://www.w3.org/2004/08/xop/include" xmlns:wsrfbf="http://docs.oasis-open.org/wsrf/bf-2" xmlns:wstop="http://docs.oasis-open.org/wsn/t-1" xmlns:tt="http://www.onvif.org/ver10/schema" xmlns:acert="http://www.axis.com/vapix/ws/cert" xmlns:wsrfr="http://docs.oasis-open.org/wsrf/r-2" xmlns:aa="http://www.axis.com/vapix/ws/action1" xmlns:acertificates="http://www.axis.com/vapix/ws/certificates" xmlns:aentry="http://www.axis.com/vapix/ws/entry" xmlns:aev="http://www.axis.com/vapix/ws/event1" xmlns:aeva="http://www.axis.com/vapix/ws/embeddedvideoanalytics1" xmlns:ali1="http://www.axis.com/vapix/ws/light/CommonBinding" xmlns:ali2="http://www.axis.com/vapix/ws/light/IntensityBinding" xmlns:ali3="http://www.axis.com/vapix/ws/light/AngleOfIlluminationBinding" xmlns:ali4="http://www.axis.com/vapix/ws/light/DayNightSynchronizeBinding" xmlns:ali="http://www.axis.com/vapix/ws/light" xmlns:apc="http://www.axis.com/vapix/ws/panopsiscalibration1" xmlns:arth="http://www.axis.com/vapix/ws/recordedtour1" xmlns:asd="http://www.axis.com/vapix/ws/shockdetection" xmlns:aweb="http://www.axis.com/vapix/ws/webserver" xmlns:tan1="http://www.onvif.org/ver20/analytics/wsdl/RuleEngineBinding" xmlns:tan2="http://www.onvif.org/ver20/analytics/wsdl/AnalyticsEngineBinding" xmlns:tan="http://www.onvif.org/ver20/analytics/wsdl" xmlns:tds="http://www.onvif.org/ver10/device/wsdl" xmlns:tev1="http://www.onvif.org/ver10/events/wsdl/NotificationProducerBinding" xmlns:tev2="http://www.onvif.org/ver10/events/wsdl/EventBinding" xmlns:tev3="http://www.onvif.org/ver10/events/wsdl/SubscriptionManagerBinding" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:tev4="http://www.onvif.org/ver10/events/wsdl/PullPointSubscriptionBinding" xmlns:tev="http://www.onvif.org/ver10/events/wsdl" xmlns:timg="http://www.onvif.org/ver20/imaging/wsdl" xmlns:tmd="http://www.onvif.org/ver10/deviceIO/wsdl" xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl" xmlns:tr2="http://www.onvif.org/ver20/media/wsdl" xmlns:trc="http://www.onvif.org/ver10/recording/wsdl" xmlns:trp="http://www.onvif.org/ver10/replay/wsdl" xmlns:trt="http://www.onvif.org/ver10/media/wsdl" xmlns:tse="http://www.onvif.org/ver10/search/wsdl" xmlns:ter="http://www.onvif.org/ver10/error" xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics">
  <SOAP-ENV:Body>
    <aev:GetEventInstancesResponse>
      <wstop:TopicSet>
        <tns1:RuleEngine aev:NiceName="Application">
          <MotionRegionDetector>
            <Motion wstop:topic="true" isApplicationData="true">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance Type="xsd:string" Name="RuleName">
                    <aev:Value>VMD 4 ACAP 2</aev:Value>
                    <aev:Value>VMD 4 ACAP</aev:Value>
                  </aev:SimpleItemInstance>
                  <aev:SimpleItemInstance Type="tt:ReferenceToken" Name="VideoSource">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="State" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Motion>
          </MotionRegionDetector>
          <tnsaxis:VMD3 aev:NiceName="Video Motion Detection 3">
            <vmd3_video_1 wstop:topic="true" aev:NiceName="VMD 3">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Area ID" Type="xsd:int" Name="areaid">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="active" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </vmd3_video_1>
          </tnsaxis:VMD3>
        </tns1:RuleEngine>
        <tnsaxis:CameraApplicationPlatform>
          <VMD aev:NiceName="Video Motion Detection">
            <Camera1Profile2 wstop:topic="true" aev:NiceName="VMD 4: VMD 4 ACAP 2">
              <aev:MessageInstance aev:isProperty="true">
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="active" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Camera1Profile2>
            <Camera1ProfileANY wstop:topic="true" aev:NiceName="VMD 4: Any Profile">
              <aev:MessageInstance aev:isProperty="true">
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="active" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Camera1ProfileANY>
            <Camera1Profile1 wstop:topic="true" aev:NiceName="VMD 4: VMD 4 ACAP">
              <aev:MessageInstance aev:isProperty="true">
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="active" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Camera1Profile1>
          </VMD>
        </tnsaxis:CameraApplicationPlatform>
        <tns1:VideoSource aev:NiceName="Video source">
          <MotionAlarm wstop:topic="true">
            <aev:MessageInstance aev:isProperty="true">
              <aev:SourceInstance>
                <aev:SimpleItemInstance Type="tt:ReferenceToken" Name="Source">
                  <aev:Value>0</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance Type="xsd:boolean" Name="State" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </MotionAlarm>
          <tnsaxis:LiveStreamAccessed wstop:topic="true" aev:NiceName="Live stream accessed">
            <aev:MessageInstance aev:isProperty="true">
              <aev:DataInstance>
                <aev:SimpleItemInstance Type="xsd:boolean" Name="accessed" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </tnsaxis:LiveStreamAccessed>
          <tnsaxis:Tampering wstop:topic="true" aev:NiceName="Camera tampering">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Channel" Type="xsd:int" Name="channel">
                  <aev:Value>1</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Tampering" Type="xsd:int" Name="tampering">
                  <aev:Value>1</aev:Value>
                </aev:SimpleItemInstance>
              </aev:DataInstance>
            </aev:MessageInstance>
          </tnsaxis:Tampering>
          <GlobalSceneChange isApplicationData="true">
            <ImagingService wstop:topic="true">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance Type="tt:ReferenceToken" Name="Source">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="State" isPropertyState="true">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:DataInstance>
              </aev:MessageInstance>
            </ImagingService>
          </GlobalSceneChange>
          <tnsaxis:DayNightVision wstop:topic="true" aev:NiceName="Day night vision">
            <aev:MessageInstance aev:isProperty="true">
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Video source configuration token" Type="xsd:int" Name="VideoSourceConfigurationToken">
                  <aev:Value>1</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="day" Type="xsd:boolean" Name="day" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </tnsaxis:DayNightVision>
        </tns1:VideoSource>
        <tns1:RecordingConfig aev:NiceName="Recording Config">
          <CreateRecording wstop:topic="true" aev:NiceName="Create Recording">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Recording Token" Type="xsd:string" Name="RecordingToken"/>
              </aev:SourceInstance>
            </aev:MessageInstance>
          </CreateRecording>
          <DeleteRecording wstop:topic="true" aev:NiceName="Delete Recording">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Recording Token" Type="xsd:string" Name="RecordingToken"/>
              </aev:SourceInstance>
            </aev:MessageInstance>
          </DeleteRecording>
          <TrackConfiguration wstop:topic="true" aev:NiceName="Track Configuration">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Track Token" Type="xsd:string" Name="TrackToken"/>
                <aev:SimpleItemInstance aev:NiceName="Recording Token" Type="xsd:string" Name="RecordingToken"/>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Track Configuration" Type="xsd:string" Name="Configuration" onvif-element="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </TrackConfiguration>
          <RecordingConfiguration wstop:topic="true" aev:NiceName="Recording Configuration">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Recording Token" Type="xsd:string" Name="RecordingToken"/>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Recording Configuration" Type="xsd:string" Name="Configuration" onvif-element="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </RecordingConfiguration>
          <RecordingJobConfiguration wstop:topic="true" aev:NiceName="Recording Job Configuration">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Recording Job Token" Type="xsd:string" Name="RecordingJobToken"/>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Recording Job Configuration" Type="xsd:string" Name="Configuration" onvif-element="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </RecordingJobConfiguration>
        </tns1:RecordingConfig>
        <tns1:Media>
          <ProfileChanged wstop:topic="true" isApplicationData="true" aev:NiceName="Profile Changed">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance Type="xsd:string" Name="Token"/>
              </aev:SourceInstance>
            </aev:MessageInstance>
          </ProfileChanged>
          <ConfigurationChanged wstop:topic="true" isApplicationData="true" aev:NiceName="Configuration Changed">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance Type="xsd:string" Name="Token"/>
                <aev:SimpleItemInstance Type="xsd:string" Name="Type"/>
              </aev:SourceInstance>
            </aev:MessageInstance>
          </ConfigurationChanged>
        </tns1:Media>
        <tns1:LightControl>
          <tnsaxis:LightStatusChanged>
            <Status wstop:topic="true" isApplicationData="true">
              <aev:MessageInstance aev:isProperty="true">
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:string" Name="state" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Status>
          </tnsaxis:LightStatusChanged>
        </tns1:LightControl>
        <tns1:Device aev:NiceName="Device">
          <tnsaxis:Light aev:NiceName="Light">
            <Status wstop:topic="true" isApplicationData="true" aev:NiceName="Status">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Light ID" Type="xsd:int" Name="id">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="State" Type="xsd:string" Name="state" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Status>
          </tnsaxis:Light>
          <tnsaxis:HardwareFailure aev:NiceName="Hardware Failure">
            <StorageFailure wstop:topic="true" aev:NiceName="Storage Failure">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Disk" Type="xsd:string" Name="disk_id">
                    <aev:Value>SD_DISK</aev:Value>
                    <aev:Value>NetworkShare</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Storage Disruption" Type="xsd:boolean" Name="disruption" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </StorageFailure>
          </tnsaxis:HardwareFailure>
          <tnsaxis:SystemMessage aev:NiceName="System message">
            <ActionFailed wstop:topic="true" client-event="true" aev:NiceName="Action failed">
              <aev:MessageInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:string" Name="description"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </ActionFailed>
          </tnsaxis:SystemMessage>
          <Trigger>
            <DigitalInput wstop:topic="true" isApplicationData="true">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance Type="tt:ReferenceToken" Name="InputToken">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="LogicalState" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </DigitalInput>
          </Trigger>
          <tnsaxis:Sensor aev:NiceName="Device sensors">
            <PIR wstop:topic="true" aev:NiceName="PIR sensor">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Sensor" Type="xsd:int" Name="sensor">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Active" Type="xsd:boolean" Name="state" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </PIR>
          </tnsaxis:Sensor>
          <tnsaxis:IO aev:NiceName="Input ports">
            <VirtualPort wstop:topic="true" aev:NiceName="Manual trigger">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Port" Type="xsd:int" Name="port">
                    <aev:Value>1</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Active" Type="xsd:boolean" Name="state" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </VirtualPort>
            <VirtualInput wstop:topic="true" aev:NiceName="Virtual input">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Port number" Type="xsd:int" Name="port">
                    <aev:Value>1</aev:Value>
                    <aev:Value>2</aev:Value>
                    <aev:Value>3</aev:Value>
                    <aev:Value>4</aev:Value>
                    <aev:Value>5</aev:Value>
                    <aev:Value>7</aev:Value>
                    <aev:Value>8</aev:Value>
                    <aev:Value>6</aev:Value>
                    <aev:Value>9</aev:Value>
                    <aev:Value>10</aev:Value>
                    <aev:Value>11</aev:Value>
                    <aev:Value>12</aev:Value>
                    <aev:Value>13</aev:Value>
                    <aev:Value>14</aev:Value>
                    <aev:Value>15</aev:Value>
                    <aev:Value>16</aev:Value>
                    <aev:Value>17</aev:Value>
                    <aev:Value>20</aev:Value>
                    <aev:Value>18</aev:Value>
                    <aev:Value>19</aev:Value>
                    <aev:Value>21</aev:Value>
                    <aev:Value>22</aev:Value>
                    <aev:Value>23</aev:Value>
                    <aev:Value>24</aev:Value>
                    <aev:Value>25</aev:Value>
                    <aev:Value>26</aev:Value>
                    <aev:Value>27</aev:Value>
                    <aev:Value>28</aev:Value>
                    <aev:Value>29</aev:Value>
                    <aev:Value>31</aev:Value>
                    <aev:Value>32</aev:Value>
                    <aev:Value>30</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Active" Type="xsd:boolean" Name="active" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </VirtualInput>
          </tnsaxis:IO>
          <tnsaxis:Status aev:NiceName="Device status">
            <SystemReady wstop:topic="true" aev:NiceName="System Ready">
              <aev:MessageInstance aev:isProperty="true">
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="ready" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </SystemReady>
            <Temperature aev:NiceName="Temperature sensors">
              <Above wstop:topic="true" aev:NiceName="Above operating temperature">
                <aev:MessageInstance aev:isProperty="true">
                  <aev:DataInstance>
                    <aev:SimpleItemInstance aev:NiceName="Above range" Type="xsd:boolean" Name="sensor_level" isPropertyState="true"/>
                  </aev:DataInstance>
                </aev:MessageInstance>
              </Above>
              <Below wstop:topic="true" aev:NiceName="Below operating temperature">
                <aev:MessageInstance aev:isProperty="true">
                  <aev:DataInstance>
                    <aev:SimpleItemInstance aev:NiceName="Below range" Type="xsd:boolean" Name="sensor_level" isPropertyState="true"/>
                  </aev:DataInstance>
                </aev:MessageInstance>
              </Below>
              <Inside wstop:topic="true" aev:NiceName="Within operating temperature">
                <aev:MessageInstance aev:isProperty="true">
                  <aev:DataInstance>
                    <aev:SimpleItemInstance aev:NiceName="Within range" Type="xsd:boolean" Name="sensor_level" isPropertyState="true"/>
                  </aev:DataInstance>
                </aev:MessageInstance>
              </Inside>
              <Above_or_below wstop:topic="true" aev:NiceName="Above or below operating temperature">
                <aev:MessageInstance aev:isProperty="true">
                  <aev:DataInstance>
                    <aev:SimpleItemInstance aev:NiceName="Above or below range" Type="xsd:boolean" Name="sensor_level" isPropertyState="true"/>
                  </aev:DataInstance>
                </aev:MessageInstance>
              </Above_or_below>
            </Temperature>
          </tnsaxis:Status>
          <tnsaxis:Network>
            <Lost wstop:topic="true" aev:NiceName="Network lost">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Interface" Type="xsd:string" Name="interface">
                    <aev:Value>Any</aev:Value>
                    <aev:Value>eth0</aev:Value>
                    <aev:Value>eth1</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Lost" Type="xsd:boolean" Name="lost" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Lost>
            <AddressAdded wstop:topic="true" aev:NiceName="AddressAdded">
              <aev:MessageInstance>
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Interface" Type="xsd:string" Name="interface"/>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Origin" Type="xsd:string" Name="origin"/>
                  <aev:SimpleItemInstance aev:NiceName="Address" Type="xsd:string" Name="address"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </AddressAdded>
            <AddressRemoved wstop:topic="true" aev:NiceName="AddressRemoved">
              <aev:MessageInstance>
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Interface" Type="xsd:string" Name="interface"/>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Origin" Type="xsd:string" Name="origin"/>
                  <aev:SimpleItemInstance aev:NiceName="Address" Type="xsd:string" Name="address"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </AddressRemoved>
          </tnsaxis:Network>
        </tns1:Device>
        <tnsaxis:Storage aev:NiceName="Storage">
          <Disruption wstop:topic="true" aev:NiceName="Storage disruption">
            <aev:MessageInstance aev:isProperty="true">
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Disk" Type="xsd:string" Name="disk_id">
                  <aev:Value>SD_DISK</aev:Value>
                  <aev:Value>NetworkShare</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Disruption" Type="xsd:boolean" Name="disruption" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </Disruption>
          <Recording wstop:topic="true" aev:NiceName="Recording ongoing">
            <aev:MessageInstance aev:isProperty="true">
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Recording status" Type="xsd:boolean" Name="recording" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </Recording>
        </tnsaxis:Storage>
        <tns1:PTZController aev:NiceName="PTZController">
          <tnsaxis:PTZPresets aev:NiceName="PTZ Presets">
            <Channel_1 wstop:topic="true" aev:NiceName="PTZ preset reached on channel 1">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Preset token" Type="xsd:int" Name="PresetToken">
                    <aev:Value aev:NiceName="Any">-1</aev:Value>
                    <aev:Value aev:NiceName="Home">1</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Preset reached" Type="xsd:boolean" Name="on_preset" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Channel_1>
            <Channel_2 wstop:topic="true" aev:NiceName="PTZ preset reached on channel 2">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Preset token" Type="xsd:int" Name="PresetToken">
                    <aev:Value aev:NiceName="Any">-1</aev:Value>
                    <aev:Value aev:NiceName="Home">1</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Preset reached" Type="xsd:boolean" Name="on_preset" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Channel_2>
          </tnsaxis:PTZPresets>
          <tnsaxis:Move aev:NiceName="PTZ moving">
            <Channel_1 wstop:topic="true" aev:NiceName="PTZ movement on channel 1">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="PTZ channel" Type="xsd:int" Name="PTZConfigurationToken">
                    <aev:Value>1</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Moving" Type="xsd:boolean" Name="is_moving" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Channel_1>
            <Channel_2 wstop:topic="true" aev:NiceName="PTZ movement on channel 2">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="PTZ channel" Type="xsd:int" Name="PTZConfigurationToken">
                    <aev:Value>2</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Moving" Type="xsd:boolean" Name="is_moving" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Channel_2>
          </tnsaxis:Move>
          <tnsaxis:ControlQueue wstop:topic="true" aev:NiceName="PTZ control queue">
            <aev:MessageInstance aev:isProperty="true">
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="PTZ channel" Type="xsd:int" Name="PTZConfigurationToken">
                  <aev:Value>1</aev:Value>
                  <aev:Value>2</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Queue owner" Type="xsd:string" Name="queue_owner" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </tnsaxis:ControlQueue>
          <tnsaxis:PTZError wstop:topic="true" aev:NiceName="PTZ error">
            <aev:MessageInstance>
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Channel" Type="xsd:int" Name="channel"/>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance Type="xsd:string" Name="ptz_error"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </tnsaxis:PTZError>
          <tnsaxis:PTZReady wstop:topic="true" aev:NiceName="PTZ ready">
            <aev:MessageInstance aev:isProperty="true">
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Channel" Type="xsd:int" Name="channel">
                  <aev:Value>1</aev:Value>
                  <aev:Value>2</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Ready" Type="xsd:boolean" Name="ready" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </tnsaxis:PTZReady>
        </tns1:PTZController>
        <tns1:UserAlarm>
          <tnsaxis:Recurring aev:NiceName="Schedule">
            <Interval wstop:topic="true" aev:NiceName="Scheduled event">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Schedule" Type="xsd:string" Name="id">
                    <aev:Value aev:NiceName="Office Hours">com.axis.schedules.office_hours</aev:Value>
                    <aev:Value aev:NiceName="Weekdays">com.axis.schedules.weekdays</aev:Value>
                    <aev:Value aev:NiceName="Weekends">com.axis.schedules.weekends</aev:Value>
                    <aev:Value aev:NiceName="After Hours">com.axis.schedules.after_hours</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Active" Type="xsd:boolean" Name="active" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Interval>
          </tnsaxis:Recurring>
        </tns1:UserAlarm>
        <tns1:AudioSource>
          <tnsaxis:TriggerLevel wstop:topic="true" aev:NiceName="Audio detection">
            <aev:MessageInstance aev:isProperty="true">
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Channel" Type="xsd:int" Name="channel">
                  <aev:Value>1</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Above alarm level" Type="xsd:boolean" Name="triggered" isPropertyState="true"/>
              </aev:DataInstance>
            </aev:MessageInstance>
          </tnsaxis:TriggerLevel>
        </tns1:AudioSource>
      </wstop:TopicSet>
    </aev:GetEventInstancesResponse>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

EVENT_INSTANCE_PIR_SENSOR = """<?xml version="1.0" encoding="UTF-8"?>\n
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:c14n="http://www.w3.org/2001/10/xml-exc-c14n#" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsa5="http://www.w3.org/2005/08/addressing" xmlns:xmime="http://tempuri.org/xmime.xsd" xmlns:xop="http://www.w3.org/2004/08/xop/include" xmlns:wsrfbf="http://docs.oasis-open.org/wsrf/bf-2" xmlns:wstop="http://docs.oasis-open.org/wsn/t-1" xmlns:tt="http://www.onvif.org/ver10/schema" xmlns:acert="http://www.axis.com/vapix/ws/cert" xmlns:wsrfr="http://docs.oasis-open.org/wsrf/r-2" xmlns:aa="http://www.axis.com/vapix/ws/action1" xmlns:acertificates="http://www.axis.com/vapix/ws/certificates" xmlns:aentry="http://www.axis.com/vapix/ws/entry" xmlns:aev="http://www.axis.com/vapix/ws/event1" xmlns:aeva="http://www.axis.com/vapix/ws/embeddedvideoanalytics1" xmlns:ali1="http://www.axis.com/vapix/ws/light/CommonBinding" xmlns:ali2="http://www.axis.com/vapix/ws/light/IntensityBinding" xmlns:ali3="http://www.axis.com/vapix/ws/light/AngleOfIlluminationBinding" xmlns:ali4="http://www.axis.com/vapix/ws/light/DayNightSynchronizeBinding" xmlns:ali="http://www.axis.com/vapix/ws/light" xmlns:apc="http://www.axis.com/vapix/ws/panopsiscalibration1" xmlns:arth="http://www.axis.com/vapix/ws/recordedtour1" xmlns:asd="http://www.axis.com/vapix/ws/shockdetection" xmlns:aweb="http://www.axis.com/vapix/ws/webserver" xmlns:tan1="http://www.onvif.org/ver20/analytics/wsdl/RuleEngineBinding" xmlns:tan2="http://www.onvif.org/ver20/analytics/wsdl/AnalyticsEngineBinding" xmlns:tan="http://www.onvif.org/ver20/analytics/wsdl" xmlns:tds="http://www.onvif.org/ver10/device/wsdl" xmlns:tev1="http://www.onvif.org/ver10/events/wsdl/NotificationProducerBinding" xmlns:tev2="http://www.onvif.org/ver10/events/wsdl/EventBinding" xmlns:tev3="http://www.onvif.org/ver10/events/wsdl/SubscriptionManagerBinding" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:tev4="http://www.onvif.org/ver10/events/wsdl/PullPointSubscriptionBinding" xmlns:tev="http://www.onvif.org/ver10/events/wsdl" xmlns:timg="http://www.onvif.org/ver20/imaging/wsdl" xmlns:tmd="http://www.onvif.org/ver10/deviceIO/wsdl" xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl" xmlns:tr2="http://www.onvif.org/ver20/media/wsdl" xmlns:trc="http://www.onvif.org/ver10/recording/wsdl" xmlns:trp="http://www.onvif.org/ver10/replay/wsdl" xmlns:trt="http://www.onvif.org/ver10/media/wsdl" xmlns:tse="http://www.onvif.org/ver10/search/wsdl" xmlns:ter="http://www.onvif.org/ver10/error" xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics">
  <SOAP-ENV:Body>
    <aev:GetEventInstancesResponse>
      <wstop:TopicSet>
        <tns1:Device aev:NiceName="Device">
          <tnsaxis:Sensor aev:NiceName="Device sensors">
            <PIR wstop:topic="true" aev:NiceName="PIR sensor">
              <aev:MessageInstance aev:isProperty="true">
                <aev:SourceInstance>
                  <aev:SimpleItemInstance aev:NiceName="Sensor" Type="xsd:int" Name="sensor">
                    <aev:Value>0</aev:Value>
                  </aev:SimpleItemInstance>
                </aev:SourceInstance>
                <aev:DataInstance>
                  <aev:SimpleItemInstance aev:NiceName="Active" Type="xsd:boolean" Name="state" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </PIR>
          </tnsaxis:Sensor>
        </tns1:Device>
      </wstop:TopicSet>
    </aev:GetEventInstancesResponse>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

# Multiple sources
EVENT_INSTANCE_STORAGE_ALERT = """<?xml version="1.0" encoding="UTF-8"?>\n
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:c14n="http://www.w3.org/2001/10/xml-exc-c14n#" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsa5="http://www.w3.org/2005/08/addressing" xmlns:xmime="http://tempuri.org/xmime.xsd" xmlns:xop="http://www.w3.org/2004/08/xop/include" xmlns:wsrfbf="http://docs.oasis-open.org/wsrf/bf-2" xmlns:wstop="http://docs.oasis-open.org/wsn/t-1" xmlns:tt="http://www.onvif.org/ver10/schema" xmlns:acert="http://www.axis.com/vapix/ws/cert" xmlns:wsrfr="http://docs.oasis-open.org/wsrf/r-2" xmlns:aa="http://www.axis.com/vapix/ws/action1" xmlns:acertificates="http://www.axis.com/vapix/ws/certificates" xmlns:aentry="http://www.axis.com/vapix/ws/entry" xmlns:aev="http://www.axis.com/vapix/ws/event1" xmlns:aeva="http://www.axis.com/vapix/ws/embeddedvideoanalytics1" xmlns:ali1="http://www.axis.com/vapix/ws/light/CommonBinding" xmlns:ali2="http://www.axis.com/vapix/ws/light/IntensityBinding" xmlns:ali3="http://www.axis.com/vapix/ws/light/AngleOfIlluminationBinding" xmlns:ali4="http://www.axis.com/vapix/ws/light/DayNightSynchronizeBinding" xmlns:ali="http://www.axis.com/vapix/ws/light" xmlns:apc="http://www.axis.com/vapix/ws/panopsiscalibration1" xmlns:arth="http://www.axis.com/vapix/ws/recordedtour1" xmlns:asd="http://www.axis.com/vapix/ws/shockdetection" xmlns:aweb="http://www.axis.com/vapix/ws/webserver" xmlns:tan1="http://www.onvif.org/ver20/analytics/wsdl/RuleEngineBinding" xmlns:tan2="http://www.onvif.org/ver20/analytics/wsdl/AnalyticsEngineBinding" xmlns:tan="http://www.onvif.org/ver20/analytics/wsdl" xmlns:tds="http://www.onvif.org/ver10/device/wsdl" xmlns:tev1="http://www.onvif.org/ver10/events/wsdl/NotificationProducerBinding" xmlns:tev2="http://www.onvif.org/ver10/events/wsdl/EventBinding" xmlns:tev3="http://www.onvif.org/ver10/events/wsdl/SubscriptionManagerBinding" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:tev4="http://www.onvif.org/ver10/events/wsdl/PullPointSubscriptionBinding" xmlns:tev="http://www.onvif.org/ver10/events/wsdl" xmlns:timg="http://www.onvif.org/ver20/imaging/wsdl" xmlns:tmd="http://www.onvif.org/ver10/deviceIO/wsdl" xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl" xmlns:tr2="http://www.onvif.org/ver20/media/wsdl" xmlns:trc="http://www.onvif.org/ver10/recording/wsdl" xmlns:trp="http://www.onvif.org/ver10/replay/wsdl" xmlns:trt="http://www.onvif.org/ver10/media/wsdl" xmlns:tse="http://www.onvif.org/ver10/search/wsdl" xmlns:ter="http://www.onvif.org/ver10/error" xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics">
  <SOAP-ENV:Body>
    <aev:GetEventInstancesResponse>
      <wstop:TopicSet>
        <tnsaxis:Storage aev:NiceName="Storage">
          <Alert wstop:topic="true" aev:NiceName="Storage alert">
            <aev:MessageInstance aev:isProperty="true">
              <aev:SourceInstance>
                <aev:SimpleItemInstance aev:NiceName="Disk" Type="xsd:string" Name="disk_id">
                  <aev:Value>SD_DISK</aev:Value>
                  <aev:Value>NetworkShare</aev:Value>
                </aev:SimpleItemInstance>
              </aev:SourceInstance>
              <aev:DataInstance>
                <aev:SimpleItemInstance aev:NiceName="Temperature" Type="xsd:int" Name="temperature">
                </aev:SimpleItemInstance>
                <aev:SimpleItemInstance isPropertyState="true" aev:NiceName="Alert" Type="xsd:boolean" Name="alert">
                </aev:SimpleItemInstance>
                <aev:SimpleItemInstance aev:NiceName="Wear" Type="xsd:int" Name="wear">
                </aev:SimpleItemInstance>
                <aev:SimpleItemInstance aev:NiceName="Overall Health" Type="xsd:int" Name="overall_health">
                </aev:SimpleItemInstance>
              </aev:DataInstance>
            </aev:MessageInstance>
          </Alert>
        </tnsaxis:Storage>
      </wstop:TopicSet>
    </aev:GetEventInstancesResponse>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

# No source instance
EVENT_INSTANCE_VMD4_PROFILE1 = """<?xml version="1.0" encoding="UTF-8"?>\n
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope" xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:c14n="http://www.w3.org/2001/10/xml-exc-c14n#" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsa5="http://www.w3.org/2005/08/addressing" xmlns:xmime="http://tempuri.org/xmime.xsd" xmlns:xop="http://www.w3.org/2004/08/xop/include" xmlns:wsrfbf="http://docs.oasis-open.org/wsrf/bf-2" xmlns:wstop="http://docs.oasis-open.org/wsn/t-1" xmlns:tt="http://www.onvif.org/ver10/schema" xmlns:acert="http://www.axis.com/vapix/ws/cert" xmlns:wsrfr="http://docs.oasis-open.org/wsrf/r-2" xmlns:aa="http://www.axis.com/vapix/ws/action1" xmlns:acertificates="http://www.axis.com/vapix/ws/certificates" xmlns:aentry="http://www.axis.com/vapix/ws/entry" xmlns:aev="http://www.axis.com/vapix/ws/event1" xmlns:aeva="http://www.axis.com/vapix/ws/embeddedvideoanalytics1" xmlns:ali1="http://www.axis.com/vapix/ws/light/CommonBinding" xmlns:ali2="http://www.axis.com/vapix/ws/light/IntensityBinding" xmlns:ali3="http://www.axis.com/vapix/ws/light/AngleOfIlluminationBinding" xmlns:ali4="http://www.axis.com/vapix/ws/light/DayNightSynchronizeBinding" xmlns:ali="http://www.axis.com/vapix/ws/light" xmlns:apc="http://www.axis.com/vapix/ws/panopsiscalibration1" xmlns:arth="http://www.axis.com/vapix/ws/recordedtour1" xmlns:asd="http://www.axis.com/vapix/ws/shockdetection" xmlns:aweb="http://www.axis.com/vapix/ws/webserver" xmlns:tan1="http://www.onvif.org/ver20/analytics/wsdl/RuleEngineBinding" xmlns:tan2="http://www.onvif.org/ver20/analytics/wsdl/AnalyticsEngineBinding" xmlns:tan="http://www.onvif.org/ver20/analytics/wsdl" xmlns:tds="http://www.onvif.org/ver10/device/wsdl" xmlns:tev1="http://www.onvif.org/ver10/events/wsdl/NotificationProducerBinding" xmlns:tev2="http://www.onvif.org/ver10/events/wsdl/EventBinding" xmlns:tev3="http://www.onvif.org/ver10/events/wsdl/SubscriptionManagerBinding" xmlns:wsnt="http://docs.oasis-open.org/wsn/b-2" xmlns:tev4="http://www.onvif.org/ver10/events/wsdl/PullPointSubscriptionBinding" xmlns:tev="http://www.onvif.org/ver10/events/wsdl" xmlns:timg="http://www.onvif.org/ver20/imaging/wsdl" xmlns:tmd="http://www.onvif.org/ver10/deviceIO/wsdl" xmlns:tptz="http://www.onvif.org/ver20/ptz/wsdl" xmlns:tr2="http://www.onvif.org/ver20/media/wsdl" xmlns:trc="http://www.onvif.org/ver10/recording/wsdl" xmlns:trp="http://www.onvif.org/ver10/replay/wsdl" xmlns:trt="http://www.onvif.org/ver10/media/wsdl" xmlns:tse="http://www.onvif.org/ver10/search/wsdl" xmlns:ter="http://www.onvif.org/ver10/error" xmlns:tns1="http://www.onvif.org/ver10/topics" xmlns:tnsaxis="http://www.axis.com/2009/event/topics">
  <SOAP-ENV:Body>
    <aev:GetEventInstancesResponse>
      <wstop:TopicSet>
        <tnsaxis:CameraApplicationPlatform>
          <VMD aev:NiceName="Video Motion Detection">
            <Camera1Profile1 wstop:topic="true" aev:NiceName="VMD 4: VMD 4 ACAP">
              <aev:MessageInstance aev:isProperty="true">
                <aev:DataInstance>
                  <aev:SimpleItemInstance Type="xsd:boolean" Name="active" isPropertyState="true"/>
                </aev:DataInstance>
              </aev:MessageInstance>
            </Camera1Profile1>
          </VMD>
        </tnsaxis:CameraApplicationPlatform>
      </wstop:TopicSet>
    </aev:GetEventInstancesResponse>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""
