voice_json = {
    "1": {
        "request": True,
        "id": 1000000,
        "method": "getRouterRtpCapabilities",
        "data": {

        }
    },
    "2": {
        "data": {
            "displayName": ""
        },
        "id": 1000000,
        "method": "join",
        "request": True
    },
    "3": {
        "data": {
            "comedia": True,
            "rtcpMux": False,
            "type": "plain"
        },
        "id": 1000000,
        "method": "createPlainTransport",
        "request": True
    },
    "4": {
        "data": {
            "appData": {

            },
            "kind": "audio",
            "peerId": "",
            "rtpParameters": {
                "codecs": [
                    {
                        "channels": 2,
                        "clockRate": 48000,
                        "mimeType": "audio/opus",
                        "parameters": {
                            "sprop-stereo": 1
                        },
                        "payloadType": 100
                    }
                ],
                "encodings": [
                    {
                        "ssrc": 1357
                    }
                ]
            },
            "transportId": ""
        },
        "id": 1000000,
        "method": "produce",
        "request": True
    }
}