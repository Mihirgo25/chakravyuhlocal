from configs.global_constants import *

REQUEST_SOURCES = ['spot_search']
LOCATION_HIERARCHY = {
'port' : 1,
'country' : 2,
'trade' : 3,
'continent' : 4
}

LOCATION_PAIR_HIERARCHY = {
  'port:port' : 1,
  'port:country' : 2,
  'port:trade' : 3,
  'port:continent' : 4,
  'country:port' : 5,
  'country:country' : 6,
  'country:trade' : 7,
  'country:continent' : 8,
  'trade:port' : 9,
  'trade:country' : 10,
  'trade:trade' : 11,
  'trade:continent' : 12,
  'continent:port' : 13,
  'continent:country' : 14,
  'continent:trade' : 15,
  'continent:continent' : 16,
}

COMMODITY_SURCHARGE_CONTAINER_COMMODITY_MAPPINGS = {
  'standard' : STANDARD_COMMODITIES + HAZ_CLASSES,
  'refer' : REFER_COMMODITIES,
  'open_top' : OPEN_TOP_COMMODITIES,
  'open_side' : OPEN_SIDE_COMMODITIES,
  'flat_rack' : FLAT_RACK_COMMODITIES,
  'iso_tank' : ISO_TANK_COMMODITIES + HAZ_CLASSES
}

LOCAL_CONTAINER_COMMODITY_MAPPINGS = {
  'standard' : [None] + HAZ_CLASSES,
  'refer' : [None],
  'open_top' : [None],
  'open_side' : [None],
  'flat_rack' : [None],
  'iso_tank' : [None] + HAZ_CLASSES
}

FREIGHT_CONTAINER_COMMODITY_MAPPINGS = {
  'standard' : [FAK_COMMODITY] + STANDARD_COMMODITIES + HAZ_CLASSES,
  'refer' : REFER_COMMODITIES,
  'open_top' : OPEN_TOP_COMMODITIES,
  'open_side' : [FAK_COMMODITY] + OPEN_SIDE_COMMODITIES,
  'flat_rack' : FLAT_RACK_COMMODITIES,
  'iso_tank' : ISO_TANK_COMMODITIES + HAZ_CLASSES
}

DEFAULT_EXPORT_DESTINATION_DETENTION = 7

DEFAULT_IMPORT_DESTINATION_DETENTION = 4

DEFAULT_EXPORT_DESTINATION_DEMURRAGE = 0

DEFAULT_IMPORT_DESTINATION_DEMURRAGE = 0

DEFAULT_WEIGHT_FREE_LIMIT = {
  "20" : 18,
  "others" : 20
}

DEFAULT_LOCAL_AGENT_ID = "5dc403b3-c1bd-4871-b8bd-35543aaadb36" #cogo freight

DEFAULT_SOURCED_BY_ID = '7f6f97fd-c17b-4760-a09f-d70b6ad963e8' # rishi agarwal

DEFAULT_PROCURED_BY_ID = '4c84b487-4964-40e9-8d8f-035f5c0f4b25' # cogo freight

DEFAULT_DASHBOARD_FCL_FREIGHT_SERVICE_PROVIDER = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'

DEFAULT_SERVICE_PROVIDER_ID = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'

SOURCES = ['tech_ops_dashboard', 'purchase_invoice', 'rms_upload', 'cogo_lens', 'rate_extension', 'rate_sheet', 'flash_booking', 'spot_negotiation', 'shipment', 'missing_rate', 'disliked_rate']

SCHEDULE_TYPES = ['direct', 'transhipment']

DEFAULT_SCHEDULE_TYPES = 'transhipment'

POSSIBLE_FEEDBACKS = ['unsatisfactory_rate', 'unsatisfactory_destination_detention', 'unpreferred_shipping_lines']

FEEDBACK_SOURCES = ['spot_search', 'checkout']

FEEDBACK_TYPES = ['liked', 'disliked']

DEFAULT_WEIGHT_LIMITS = {
  '20' : {
    'free_limit': 18.0,
    'slabs': [
      {
        'lower_limit': 19,
        'upper_limit': 1000,
        'price': 200,
        'currency': 'USD'
      }
    ]
  },
  '40' : {
    'free_limit': 26.0,
    'slabs': [
      {
        'lower_limit': 27,
        'upper_limit': 1000,
        'price': 200,
        'currency': 'USD'
      }
    ]
  },
  '40HC' : {
    'free_limit': 26.0,
    'slabs': [
      {
        'lower_limit': 27,
        'upper_limit': 1000,
        'price': 200,
        'currency': 'USD'
      }
    ]
  },
  '45HC' : {
    'free_limit': 26.0,
    'slabs': [
      {
        'lower_limit': 27,
        'upper_limit': 1000,
        'price': 200,
        'currency': 'USD'
      }
    ]
  }
}

OVERWEIGHT_SURCHARGE_LINE_ITEM = {
  'code': 'OWS',
  'unit': 'per_container',
  'name': 'Overweight Surcharge'
}

ROLE_IDS_FOR_NOTIFICATIONS = ['70710ab2-0f80-4e12-a4f5-d75660c05315', 'dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb']  # Supply Agent/Prod_Data Operation Associete

LOCATION_HIERARCHY_FOR_WEIGHT = {
  '' : 0,
  'seaport' : 1,
  'country' : 2
}

CONTAINER_CLUSTERS = { '40_40HC' : ['40', '40HC'] }

PAYMENT_TERM = ['prepaid', 'collect']

DEFAULT_PAYMENT_TERM = 'prepaid'

SPECIFICITY_TYPE = ['cogoport', 'shipping_line', 'rate_specific']

DEFAULT_SPECIFICITY_TYPE = 'shipping_line'

TECHOPS_TASK_ABORT_REASONS = [
  'Sid Cancelled/Changed',
  'Port Currently not served'
]
# changes to be done ask rishi....
RATE_ENTITY_MAPPING = {
  "6fd98605-9d5d-479d-9fac-cf905d292b88": ['6fd98605-9d5d-479d-9fac-cf905d292b88', 'b67d40b1-616c-4471-b77b-de52b4c9f2ff', None],
  "b67d40b1-616c-4471-b77b-de52b4c9f2ff": ['b67d40b1-616c-4471-b77b-de52b4c9f2ff', '6fd98605-9d5d-479d-9fac-cf905d292b88', None]
}

VALID_UNITS = ['per_bl', 'per_container', 'per_shipment']

EXPECTED_TAT = 6 # HOURS

DEFAULT_LOCAL_AGENT_IDS = {
  "541d1232-58ce-4d64-83d6-556a42209eb7":{'platform_config_constant_id':'3617e7ea-fc4f-4478-aea2-651fcb0ec1e6', 'value_type':'default', 'value':'5dc403b3-c1bd-4871-b8bd-35543aaadb36', 'display_name':'COGO FREIGHT PRIVATE LIMITED', 'status':'active'},
  "default": {'platform_config_constant_id':'3617e7ea-fc4f-4478-aea2-651fcb0ec1e6', 'value_type':'default', 'value':'5dc403b3-c1bd-4871-b8bd-35543aaadb36', 'display_name':'COGO FREIGHT PRIVATE LIMITED', 'status':'active'}
}

ELIGIBLE_SERVICE_ORGANIZATION_IDS = {'ids':["1f868ca6-0285-43db-947c-595481cb02d5", "9f5a3379-608d-46db-b26a-49b7cf1800ee", "58674bea-31d8-46c1-86d4-24b9e2a1c9b3", "866bab88-49b0-4171-9b67-fe4e5e9bcd55", "54cac829-2bc7-49ec-9ab0-712384a36c90", "c2c17700-10fe-402a-9ab2-87659671d57f", "5d1242af-426a-4972-9819-a4f8ac295282", "56e12144-54f0-4879-9fe9-663d182d18fd", "0b3a6f7e-c1b3-400e-a146-d5a5b360b4ef", "fdcbd41c-897d-4c5e-8b95-1781d4b4c7b6", "3450eff4-95a1-4bbe-a6e7-3b0e9094b81b", "ead0eec7-305e-4038-a67e-a5557c509872", "06db0e42-c290-4be5-bc66-c19dfc7a7d17", "91955b8a-7ea6-47dd-a549-504f74b5ccf7", "82f9904c-2b84-4258-97d7-8df043548648", "13b8a62c-f56f-482e-8644-7dc5829b71b1", "8af78e36-9c12-4dc6-b2c6-eb1bf21f2b5b", "f1d9e505-24dc-40e3-8b7f-b121eb91f088", "049ccba8-02fa-403d-a9e2-2bdaf3030bec", "5cf50ac4-ca2c-4a8e-87d9-e49bd28969f0", "6fd099f9-c856-42b2-a3e9-7ba047d452d3", "d04c0035-2e91-4fd2-a588-158a0338e654", "eaec4ae0-1f54-4630-9632-d4f23ba3615d", "100986f7-91d8-443f-a3c5-c5ccd62c204e", "ae3e9dbe-7ac3-472c-86da-c928271cdd28", "b5268e8b-86f4-495b-9f68-183ac712299f", "3277911a-0114-4521-9d8e-0ea4cb5c3e5c", "31b412e4-8891-4241-b0cf-1e25edb9c8dc", "553c9064-c82b-4a4d-b9ad-ce750671e3f9", "f278ab12-90a1-4a18-9520-517ff6b2fe0d", "e328c166-f15d-4918-b983-a34015b28b69", "f768b82b-8f00-4877-b3e9-a94dfb3a5ebf", "a10192fa-5e1d-437f-aa67-ec6967cc68c8", "fc3826a9-596d-4a67-a16a-7f15f3501464", "764ca96c-b69e-4d1e-913b-b32557d59079", "1cba977b-b649-4e50-94b5-f06b878446bb", "9f2f0529-2ec6-4cf6-9d96-7ccc0ae33742", "d60339d0-103c-4e14-9cd0-79f116687451", "5dc403b3-c1bd-4871-b8bd-35543aaadb36", "d64c94d7-c3e4-4493-b8f2-854530ed6182", "02a7e087-e9ed-4193-8671-52b057d880de", "3b5e5574-85c0-4634-a468-2b1638c26942", "7978885d-83dd-4bbf-8350-25bf92b42814", "0badfe28-5fd0-41db-9a3f-53040e448b90", "79436ba3-5507-4f1d-a178-d81301f720c3", "7aa9008b-4a14-43e1-87db-609f88766f8a", "c1ed5fd9-b0b6-420b-a90a-c04ec545a168", "78103eb9-4795-4a39-af05-c5305aab000d", "13a27bec-daa3-4378-bbf5-c72028267783", "85a5510a-d93f-4cce-bcf3-5e64d35313a2", "d81f8942-628c-4e84-a464-c1b8cf7575a7", "f4550ffd-aeec-47ac-a6f7-e9d049ad042c", "47b692c7-65c9-48dc-ba70-2bbabb4fdafb", "99f840be-170f-4ced-86df-625667c41a04", "7bd9b0d1-34f3-4603-a3d3-02f426b55126", "576e396d-80f5-4349-b9d3-f2160553fd8f", "2f05784e-a313-4768-9715-da7804de36c3", "c01bc8bc-01d9-47fc-8595-12afadc6caab", "d4e3979a-b943-4221-bab9-49b98e661d4c", "f8bac357-4c4b-45ec-b083-ddb4c71ff33d", "5c10e404-6bfc-42ce-9214-1bf726f246f2", "dcef9ba6-7aca-4327-8956-e6bb61006c82", "ca5f3c0a-782c-4de0-8fdc-30502fc4fb72", "aa939528-e66c-429c-b633-1be5502e5992", "4e75da2b-5b91-4ec2-8b42-fd0efcf7baed", "558158f8-8243-4793-ae17-fd93bc07ff41", "a400bd24-cd29-4050-9cd6-b6fb522c70d7", "0f192e46-c3da-4610-8eff-de8281fcc8ec", "7dd09d9a-3c7e-43c2-8e08-633c54a8df16", "166271e8-60b8-48f8-b985-2c6315bd2a9e", "8f973f06-12a1-45e3-8897-83f8f2fa7acb", "d1c4721b-4104-4e23-8e7e-ab2e1ee1c47a", "d779511d-bbda-49ba-8bd5-857281676ca9", "727aed6d-6ff5-4451-9ec0-f2ed87ca6255", "12613011-9002-48d6-ab4a-12ce2cedc0b5", "200334e7-0968-4dac-826b-22ae166b6380", "b7ff4d05-170e-4065-9072-4537374c17c9", "3bf33f3a-b521-4558-92f3-be1e3718640c", "04f2c5a4-59f9-4398-866b-2baf39eec8b9", "2d0f8cc8-41ff-4f58-9b7a-99ecbf6ca4c5", "11110bcc-4d07-4c00-85d0-bca07b1ecae9", "9d276172-e264-475f-a064-c53b0d435a0f", "a9829f05-2ffe-4337-8a44-0544ee4003a6", "46417589-2980-4d9a-ba0f-e47b9835cd1d", "5a7f46d2-a070-4529-b7c3-0aae517d19ce", "829bfa50-943c-48fc-bc63-4a470a0e5707", "3ffa0077-4fa2-45d8-b6e3-744f2b7bee3c", "e0773597-ea0f-4a7c-8b6a-f3ad16b88c9c", "2a58f53c-0946-4038-82bc-eb489c0cdadc", "27bcb8f1-fcd8-43f7-9fa2-327e5d416d46", "8b692994-cbbb-4d37-a834-44bb872480cc", "edc2bea2-8c65-4efb-b36e-97aeeea42227", "251d3585-c9cf-4fab-8a56-736f4f9f3db6", "299423d7-3380-4077-9f6a-8296091ebb95", "5caccf89-c601-497f-9663-3be845978fb3", "811812cd-82d9-4775-a584-2a6a2fe528ea", "ad041e69-35fb-4b5b-bffe-05bbb1a11c86", "66a1d4bb-8b53-4ea5-bdd1-96814e7a67ca", "e6c15f28-aee5-4b29-9687-b3913388382d", "ecf89f4c-8853-4b4e-8b03-2cc27ee361da", "80f534d0-4482-4ffc-9e66-769e3593ab73", "14ff1c5e-2cae-4fcd-81b0-2c4018439870", "e994c833-075c-404f-bf74-b7246e2d7411", "5fb53278-2792-4e10-a061-9f80f813d4c1", "48f86f51-1d25-4dd6-bb5a-5466f8a63343", "3dcd0fa0-30d3-4cf3-87ee-c85ae54ecf5e", "6d813011-e299-4419-a16e-4a1ee90c2d3f", "e70936e2-0448-4f8a-9274-3caeb4272efd", "ef75654b-fcfd-46ef-b186-f8b789442ea1", "310c4e6c-423f-4f99-acf7-b75ef886e4db", "cd9af432-ffd0-4615-a11a-4abebabba749", "60c82f66-acc1-4281-beb4-adad83dded52", "a06785b3-fbf6-4650-b85f-dfe4cc343c72", "13a229ec-dd96-4dca-8c4a-88a74a4341fa", "254391bf-5f1d-49e7-9b35-4b0a2798d29b", "670b32c9-6da2-4f28-8fe7-9f69d250576d", "ee97fccd-8b5f-45eb-853b-f528d9b081d2", "3313ed29-18e0-435d-bd9d-ba3e3d10004e", "2dd056a9-7b02-428c-b1ea-08482811b5fd", "37b58ceb-93dd-450b-926b-2608d07715d9", "a2c6defb-6e0a-4e98-ad51-ab3978d4dc28", "bb600a25-6f05-4d3d-bd33-164112a64063", "99446a15-05ae-4b77-bb97-3cea83481937", "ab9aed78-ff9c-4750-b5f1-6cfa8c42b815", "1966f326-08f1-44ac-9168-526d74f72349", "9d3264f6-09f0-4f8f-a462-921805395a07", "cf0736a6-748e-4cda-bc92-ab46bbdd0b62", "56065afb-8565-4293-938c-f0e37d7fd7ad", "5f985f59-c96f-4d0b-bdd7-88ba13aa38fd", "1c2361d1-f0fc-4b06-9fdc-6bb3a759ca9d", "82c15b0c-6050-4e04-8741-42382d964c89", "46c593b7-e34f-4d6e-bf00-41cff4514d90", "f85d13a0-cb04-4947-b010-1fb9835a47ee", "014e44af-74f9-4365-bf47-a02718124d06", "606997c0-e9fb-4d3b-857a-8aa1af94731c", "99afb3a2-bcfb-42c7-b185-a04a64e97993", "e7c963c8-05b1-49e2-a13f-a5b70ded2ab1", "a40a6990-d415-40db-826a-230566829d47", "f5e2d1f0-759b-40ca-a6c4-04e3b3818973", "c7f76e93-a9b8-4837-b36d-b1ba576323e4", "f8afb084-b90a-4586-8bc0-454916bdc4f1", "f7859b14-3f6b-47f0-b688-1d99c512f752", "6d07725e-5741-4db9-adfd-1317e1b579cf", "37528242-b710-4179-b12f-20895244414d", "609728e1-7cc6-490d-ac2f-fb9a767052fd", "7199a9a2-cde7-4bbc-b5bc-5bcbb4d82159", "0ae31db4-0c13-4a18-a66e-7b410167fb57", "27b22e43-ae23-4afb-9fb0-e2be3d8293e7", "215778c8-0993-454a-84c7-4294305ee483", "65f211ed-75e7-45c1-bdf0-d3b913f1a04c", "f7dd8091-20a1-4d68-8832-7968cd879446", "5dbc4e56-5ecc-4c88-acfe-9f1a0d013651", "14f99867-ae8a-4284-ba39-40ba3066846f", "a58feec2-334b-4f9e-a759-10f0376a3d20", "d5a347cc-0ed9-42e9-9191-2b49434ccd1b", "bf8eeada-2d45-4c37-a13d-26b0a3dcad3c", "7c779ade-d49f-4273-9359-7665ff500c14", "09e4392e-1cba-4432-948d-8fc2201c39eb", "9fc775a6-cdb1-4e25-b686-1da37bc34607", "af900cad-0a2b-45f7-8c4d-80f0c3c9b1c1", "32177483-22df-45ee-955a-285abe3966ae", "3b00bb76-502f-4f41-b4fd-3f85a6699417", "6a7033ca-b49e-40cc-b13e-b9fd8af4d30b", "c18bc16a-02a3-4e18-a256-6d72b123ccb6", "8e3eaf39-e666-453c-a90f-20e3c3e9ea80", "01573c7a-b0d1-479d-8050-e743f0918a81", "96e672c9-b718-4ede-abdb-9f72b34baad4", "f1ec8bfa-40f5-4f4a-ac9c-b70731e0036b", "df4a03ef-eaf9-4bc0-b6de-ce837457dc02", "908ee101-b69c-42b1-97c2-73380e31e8bc", "001a962c-0cf6-40cc-a222-f063ac994b87", "fe5aeda1-81f5-4cd0-9917-c6a6ad8ead3c", "a02ac6a6-baf8-439d-b832-154f8fa4fb27", "9ee2d806-eb31-4cef-8197-08b6fd915417", "ba9e9689-7cb3-4bde-8b22-9c0d7ea7508f", "53fe3937-91a7-4f4d-befe-98c44976ab86", "515faf81-845d-427f-bb04-6248e07c5713", "4881d496-4092-492a-b7a8-30093f21243f", "4516addb-fe7a-4acb-8c11-cacb6219a979", "c57bccd9-aefe-4cb9-a0d4-46f0b4c4dbed", "4fdf2958-f92a-4e54-8409-65843fa88c4c", "35eec977-8030-4493-afe8-deabc5df416c", "931fa7a3-7907-40e5-85bd-eaccd007d004", "231d8909-28e9-4889-9d64-313234162f38", "9e6bb95b-476b-442e-a52b-6dd8541cd8f9", "210f66f2-cba1-4cb2-8abc-56290ddef139", "b9fca860-cede-499e-a5c6-0fa2c1f64917", "536abfe7-eab8-4a43-a4c3-6ff318ce01b5", "94772af2-5da6-42cc-84ae-f818524e58d8", "e00bbe57-bedf-449f-bf0c-561350334332", "8433173f-23a4-4474-ab21-a0d1afe62dde", "79d9b147-ba11-48fb-a5a6-60be3bf9f2e4", "11ba2bb8-c218-4c7a-bd4f-07ebc833dddb", "3650ae4f-6c49-49c8-b554-efe3c63279fc", "54b8a110-184c-4093-9f6d-9a23de59ea7a", "f5accc91-f158-4c7b-a205-5769ce54db3b", "d0da16c4-cb8e-4bdc-908d-2036cb575819", "4ef56c0b-aa63-4ada-a1c6-b481629af785", "1254af36-7ac0-4f58-acc1-6e1d64015ff6", "f20a0b20-4f83-4066-a9fd-d19a3e319468", "34501565-6a00-48cc-94f7-302918d1a6f0", "b175b634-153f-4cb6-a5da-eb5be487ade4", "a1f31893-8f0c-48b8-84d1-b72e6a30420a", "f2da51ef-bf63-4e3e-be9b-1c44aac6c4eb", "c7e3346f-23ee-4500-b7ac-8e28a6a3133e", "0ea14cd1-1360-4ccd-ba00-6175b1f6d201", "f92ce6f5-2d63-4e27-8cc5-e80d5ab7c12f", "0d49f839-3251-4e73-95c4-af2228e58adb", "3934c67a-8a78-4485-8636-f9427c640bb0", "aa2f1df7-da97-4f78-9bc9-f1542986b7ea", "d5e59f98-bfbc-408c-9b84-54ffd679eb13", "ca42c9cb-f539-4cac-a7b8-c6e7c48c097c", "9aca30ee-6081-4ef2-ab7c-59b168626285", "b6e99bdf-66ed-4c0a-8b7d-da517649c41b", "a0884b13-d39d-4d3c-8157-83a60706a743", "dd7517db-e3b9-43bb-b4fe-95faf225835e", "7197fb9d-c481-44c3-948f-c5a3ced54ae0", "ad77569f-a0ec-4403-bda5-aed9e029b1f6", "3dd89bce-daa5-48b1-9dcf-146c6d67fa75", "3976b7c3-f66e-43e4-8fef-c7eb1ab1a172", "e4186c31-ddab-4440-a44b-1e685bf37bf5", "f836618e-7dba-4d95-95cb-aacb7c87f8b8", "e0b9ebf5-5851-48dc-ab58-338f1677c7bf", "17b2a06b-aab0-464e-9cdc-956264a6f649", "9dd2a198-f283-40cc-907c-d9413c564cd4", "20347b4b-5180-44f6-8fa3-28382f4b052b", "25f8f25c-7573-4dd6-a2f8-8dd9c0f1bafd", "67eed12f-b5fd-46f9-b787-753ee5e62a85", "c46b9f9d-7856-4a9a-8a67-4726c5da6dc3", "0bf85e28-b90b-45b3-bd27-3c9bad9b4450", "ca153ed4-d822-420f-8173-94b907af0530", "2e365108-02fd-4e00-bbf3-a47d2e27ba7e", "5a2d1536-2d59-48da-b761-723fca346f96", "4b76bfe5-b6cb-40c0-9d8e-da5b8c496a40", "6eb2be3d-f5c1-4ca6-9707-3f3fca4a8bda", "7c481b6c-e044-49ef-984c-72eac3279477", "e66aa2f2-9d74-411b-8530-58ef874a885d", "e2940f15-9bf3-4181-8f88-3c18dcd1b7d8", "8eb54b84-694e-46b8-8e45-c6e1325c1534", "ee989756-9aa2-4c30-b94e-711d6085b8c7", "594c660c-a32a-42d9-b088-2cc88b9b9a4c", "3f4ae246-2d25-44c2-b41d-9e5aad963fb9", "deed690f-7a04-4fb6-9dd0-aa0856931cf4", "524b77e1-eef3-4334-89f5-5bccf84e3b2b", "0dc9b361-3fb2-4b98-b74c-310f72850850", "76ae328a-74f3-479a-96dd-ba144958085f", "284ecb76-21f4-4502-96b0-fbe09f2bdf3d", "cee4bd45-ddf3-4bc7-becc-1f7b7a2c486a", "9226bb0f-2c1f-4648-a19d-b6353180535c", "fd29bf70-a326-48a4-9df0-65e41cf89068", "53369ee6-4778-4225-aca1-1a3d0c4a24e4", "47787a34-f6df-4ac6-8479-4b7fc81f3763", "b3b42fa2-3ebf-48ee-8d6f-78b1f5056a7f", "05f65737-7290-465e-8819-32437bf3eb85", "7304631a-8b87-423f-a6d8-c985b2abd3a0", "94feb336-3765-4b64-9048-0529f656e413", "72e650a1-4681-4d5c-8e25-205aff48008a", "6d72d07b-0a20-43b8-ab14-3057f2c10029", "3158799d-1bd1-4429-b459-dd2216c48831", "3a5d1e27-4505-4ac6-abed-3e86ec05212d", "fd2e7497-cbe7-4495-a8e4-b08a3ee050e9", "06085d9d-70a2-432f-a3ea-6d49b8ece62f", "811435f2-8f5d-45a2-8128-7744397a7f57", "3bf23dab-8f6d-4134-bf9b-d7719c83f8c0", "0209251a-61ee-46fc-ae96-cb2fa861a3ae", "fb110498-5b69-4781-b396-c90c02532716", "ce9b5260-7662-4dac-a250-ddfa1cffe166", "f52d259c-2a24-4d69-aae2-d57c65958012", "9183489b-8da8-41f4-987b-b14f84ad8321", "f1fe36e9-7900-4cb2-889a-602ceba9fdf6", "e73f8f65-167b-4710-943b-7eb5eac4f768", "18002595-c5e6-4a33-93b7-81d5b3307a72", "c26bc870-1aea-4265-93d4-26f03fb00ff2", "9bb8a24f-60ec-4fd8-82dd-a3039c406ebf", "9a383e1c-2c2f-470f-8081-1924427cb628", "e9c0b3a1-e644-482f-a961-0772bd0d4837", "319a6470-d684-41b4-ab9c-f6efb4d18f27", "e5d83e86-d512-414a-9d94-3415a617b161", "53ef481f-24cf-4db1-97f0-2e78670d9b15", "0e83cb7e-c910-47c7-9149-1dd252fc52d7", "879f8b15-954d-41d0-a9f2-21ac50f882df", "c4ff43f9-dd96-4ee7-a1a3-bdb8870f6a61", "72abe9e0-c5d1-4b5f-956f-d5dc335b309a", "667c82f7-9a71-4d1a-b44b-d4f1caae5e84", "358a4b64-119a-4d37-9e8b-9380a5b8a9a5", "12d2168f-be69-4d2b-96ab-3f2fbae3efd4", "c3fe504a-55d2-414e-8821-fe63082bd156", "5eb9371a-fcc3-4cea-bac2-2e71d280e757", "4dea482e-5005-466a-abaa-6d281b493740", "4a4a1489-b187-4f1b-af7c-c717b1834f42", "6cfa1f71-24a8-4396-8646-0da35c4adc6c", "0f97ba0a-5446-4b6c-994c-2e458375f9e9", "ff0e9379-bd8c-4816-8dd9-38c6de61cbfa", "4ddf0830-43f1-4b3b-a9d9-0655819735ae", "7bd9af9e-f770-47a5-8a2f-57cdd964f7b5", "13ddb234-3ac3-446f-b492-bc0b6ba85024", "870138e5-5d7b-4490-8dca-d0af63219d7c", "27d64e1d-ba08-42cb-8755-82d021ce0b02", "3be5a46b-256d-4d9b-8e95-e6ac888c6187", "47b7760c-c7b4-4edf-be7b-637cc97b707b", "54e1fe40-10ae-4ed0-a8da-8be4d48d19e2", "c47f4c43-2a21-4718-86c5-01836929fa6c", "a7249dad-2a8f-42c8-9713-3c3e1cc99b41", "80f25e33-8539-49a6-af91-144c4b19064f", "e4bda6a3-8caa-40bb-b8d3-f1fee32b7b54", "1a082870-106b-4295-ac5d-fb82865e4122", "f2ab42cd-93cb-4630-817d-a2e8b87bbcb5", "ff216e28-ef1d-4017-9a73-26e378443b1e", "2a0d6457-682f-41e8-98d1-845bb3324479", "f64fba0c-59ef-4228-8457-1ffd2b866cdf", "0d13a8f8-75bd-4b58-b0f8-7029b52fc582", "832818d3-25c0-43e8-9ba1-607f55d73bd9", "32b4dcd8-811f-42ae-84d3-87751762eaf1", "d761d579-9369-4abc-ab0c-8734f05c21a0", "b29555c2-210e-461b-ad19-42afd6c9d2aa", "714fea8c-f361-42f1-b24b-aa2edb93a287", "e97766b0-94aa-4a05-ba4c-094d212302d7", "ecfed418-9bfb-402a-bdb6-faa1fa91f81f", "5b7bf211-f31f-41fb-82d0-101851ed0846", "ab9c2d91-edad-4e23-8d30-bfa80bd755f5", "e4b73b27-0e4b-44f5-bb18-e185920729fc", "e749f711-ffc7-4c3e-bec3-92d908844227", "98044f1a-bbb9-4274-b9a7-4e0ce5f4d33f", "f19a4512-c2ab-499e-bc04-7a18b1c9782f", "c80177bb-7d61-4dec-8368-ff114e422acb", "23ce6213-db05-4128-9790-5eee9e1c1892", "153e07b7-0de5-451f-b494-f7e323385719", "6de02113-a109-4bda-be1e-d1bf35ba961c", "5d90c90a-43bc-4f3c-8fae-02146d965dfc", "6fd4573e-874d-4042-a3fd-391ca3bdb777", "f7667300-6ec8-4e88-8bfe-0afc35a3196d", "c2708abb-9693-4c87-bd15-abd7252f8a50", "2668d77e-e5fd-4746-9418-745d1468b465", "db6e1e05-8305-4563-9e3e-8f506dc24f40", "21b79fb2-51b4-43c4-a482-c11f8aa7385a", "82a03079-33b7-435b-8fdc-69b2f006cd5a", "c38e7f45-8024-4536-8cae-48ec7b959065", "ea3d385f-1a65-45df-a1fe-d8aad253b9aa", "621f7b0b-6b12-42a2-98da-52a70c73653a", "89ed1b9a-567f-4124-90cf-61a6ad0b2885", "b631da56-59e6-4ece-bdf4-75daf92f59d0", "29421589-de02-4c36-b680-abc2502ed028", "3363caf8-5acc-4559-b9d4-cd8290b578ef", "9f9daa7e-8575-411a-86e9-5f8e2fced580", "72c0ee64-b4c3-481b-ad39-6cdf9dc47bc9", "ce47a064-3d53-4071-9689-40351dcedce0", "3d3623d4-e330-4057-a7ce-78255a370feb", "ddb47314-3356-47d3-b077-2d45ae4da3ad", "f380b69c-f58b-4c9e-b156-79fd249fefd2", "260ee7ed-eecc-4481-8db4-d51bd28860be", "b94fd5af-1154-4ced-b30c-8651f84a4eaf", "bb448532-5ac0-45de-b226-c6b71015be00", "d9dca7c0-e9f8-49bc-affe-a92276d3a7e5", "3f54cf11-a0a0-4be1-8e7f-074fc2786190", "7b43ae1a-ede0-4b6b-abad-77a5fbde3317", "03f6764a-6da8-48dd-b613-f74f42d76d78", "33a92caa-0423-4ec6-8a07-9e3cb45b1fd1", "35bf7faf-0103-44a5-a3ee-5135d28901e4", "448c138c-f58d-4dff-897b-eefc1f4b851c", "88c1958e-0ae9-4391-8e3b-d11552d72c69", "4c2dfeba-c715-4614-8a93-e051a270981d", "641a4e08-f62e-4f31-82a1-70ca40b989ef", "39545ada-9dfc-4e29-aa8f-7bcd718257be", "c8b7266e-d304-4a39-a83c-8d56a9f74508", "e8485d0e-b7e8-44c4-8e45-25775b6785b1", "8eb1488d-b5ce-4eda-9859-82096cb729e5", "103761d0-adef-47f2-ae84-b01f02da586e", "521ee5f6-117d-4aa5-b589-523cb07cca3b", "66ccd346-b095-4feb-be81-1f5ff287d7be", "51108850-f8cb-45cc-8f89-37cabdc5c2c9", "22ac6107-d2aa-45bb-87ea-302575f9ab07", "9f0f698e-e0ea-4b84-b695-34f81b0495aa"]}

SHIPPING_LINE_SERVICE_PROVIDER_FOR_PREDICTION = {
  'c3649537-0c4b-4614-b313-98540cffcf40' : '9f9daa7e-8575-411a-86e9-5f8e2fced580',
  'b2f92d49-6180-43bd-93a5-4d64f5819a9b' : '9dd2a198-f283-40cc-907c-d9413c564cd4',
  'fb1aa2f1-d136-4f26-ad8f-2e1545cc772a' : 'f92ce6f5-2d63-4e27-8cc5-e80d5ab7c12f', 
  'a2a447b4-0ce5-4d3c-afa9-2f81b313aecd' : '96e672c9-b718-4ede-abdb-9f72b34baad4',
  '9ee49704-f5a7-4f17-9e25-c5c3b5ec3d1d' : '0bf85e28-b90b-45b3-bd27-3c9bad9b4450'
}
#Maersk, cma, hapag, msc, oocl