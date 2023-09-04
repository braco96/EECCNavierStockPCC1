version: '3.3'
services:
    satelitalmlacolite:
        volumes:
            - '{input_filepath}:/input'
            - './acolite-output:/output'
            - './settings.txt:/settings'
        image: 'acolite/acolite:tact_latest'
