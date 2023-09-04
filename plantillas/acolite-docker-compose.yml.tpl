version: '3.3'
services:
    satelitalmlacolite:
        volumes:
            - '${INPUT-PATH}:/input'
            - './output:/output'
            - './settings.txt:/settings'
        image: 'acolite/acolite:tact_latest'
