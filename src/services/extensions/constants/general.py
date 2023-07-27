commodity_mappings = {
    'DGR': 'special_consideration',
    'Equation': 'general',
    'Fresh2': 'special_consideration',
    'Fresh3': 'special_consideration',
    'Pharm15-25': 'special_consideration',
    'Pharma2-25': 'special_consideration',
    'Pharma2-8': 'special_consideration',
    'Pharma2-8°': 'special_consideration',
    'Dimension': 'general',
    'EquHeavy': 'special_consideration',
    'Perishable': 'special_consideration',
    '': 'general'
}

commodity_type_mappings = {
    'DGR': 'dangerous',
    'Equation': 'all',
    'Fresh2': 'temp_controlled',
    'Fresh3': 'temp_controlled',
    'Pharm15-25': 'temp_controlled',
    'Pharma2-25': 'temp_controlled',
    'Pharma2-8': 'temp_controlled',
    'Pharma2-8°': 'temp_controlled',
    'Dimension': 'all',
    'EquHeavy': 'other_special',
    'Perishable': 'other_special',
    '': 'all'
}

surcharge_charges_mappings = {
    'SSC':'SSC',
    'FSC/MIN':'FSC',
    'XRAY/MIN':'XRAY',
    'MISC/MIN':'MSC',
    'CTG/MIN':'CTS',
    'AMS-M/AWB':'AMS',
    'AMS-M/HAWB':'HAMS',
    'AMS-E/AWB':'EAMS',
    'AMS-E/HAWB':'EHAMS'
}

airline_ids =[
    'e9a8f35c-3b78-4904-bc0e-e01af2dcff48',
    '82b7e744-19b1-4b74-9721-fb68d15ff4d6',
    '05b60693-2f45-43cd-8771-85d0adbde5e2',
    '01216d9f-0b8e-442f-9ffa-c704d8925898',
    '67af974c-596b-4709-9fde-e0955fe09a5c',
    '83af97eb-09a7-4a17-a3ca-561f0bbc0b6f',
    '63c8381e-b879-46c0-a908-49e4dad25867',
    'b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc',
    'e422bb59-3074-422d-bf9c-51afe93cc968',
    'eddc9ad8-62f6-4445-bb37-4fce5d284ed1'
]

airline_margins = {
    'e9a8f35c-3b78-4904-bc0e-e01af2dcff48':0.05,
    '82b7e744-19b1-4b74-9721-fb68d15ff4d6':0.05,
    '05b60693-2f45-43cd-8771-85d0adbde5e2':0.1,
    '01216d9f-0b8e-442f-9ffa-c704d8925898':0.05,
    '67af974c-596b-4709-9fde-e0955fe09a5c':0.05,
    '83af97eb-09a7-4a17-a3ca-561f0bbc0b6f':0.025,
    '63c8381e-b879-46c0-a908-49e4dad25867':0.05,
    'b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc':-0.25,
    'e422bb59-3074-422d-bf9c-51afe93cc968':-0.3,
    'eddc9ad8-62f6-4445-bb37-4fce5d284ed1':-0.1
}