const sendRatesToRMS = async (data={}, endpoint)=> {
  const url = `https://api.cogoport.com/fcl_freight_rate/${endpoint}`
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data)
  });
  await response.json();
}

const getFromWebPage = async (source) => {
  const [tab] = await chrome.tabs.query({active: true });
  const response = await chrome.tabs.sendMessage(tab.id, { rates: source });
  // do something with response here, not outside the function
  return response
}

const getFreightLookRates = async ()=> {
  const statusEle = document.getElementById('status')
  statusEle.innerText = 'Adding Freight Look Rates Please wait....'
  try {
    const response = await getFromWebPage('freight_look')
    await sendRatesToRMS({ rates: (response || {}).rates || [], destination: (response || {}).destination }, 'create_freight_look_rates')
    statusEle.style.color = 'green'
    statusEle.innerText = 'Rates Added Successfully....'
  } catch(err){
    statusEle.style.color = 'red'
    statusEle.innerText = 'Some Error Occured Please try again after sometime....'
  }
}

const getNewMaxRates = async ()=> {
  const statusEle = document.getElementById('status')
  statusEle.innerText = 'Adding New Max Rates Please wait....'
  try {
    const response = await getFromWebPage('new_max')
    await sendRatesToRMS({ rates: (response || {}).rates || [], destination: (response || {}).destination }, 'create_new_max_rates')
    statusEle.style.color = 'green'
    statusEle.innerText = 'Rates Added Successfully....'
  } catch(err){
    statusEle.style.color = 'red'
    statusEle.innerText = 'Some Error Occured Please try again after sometime....'
  }
}

const getWebCargoRates = async ()=> {
  const statusEle = document.getElementById('status')
  statusEle.innerText = 'Adding Web Cargo Rates Please wait....'
  try {
    const response = await getFromWebPage('web_cargo')
    await sendRatesToRMS({ rates: (response || {}).rates || [], destination: (response || {}).destination }, 'create_web_cargo_rates')
    statusEle.style.color = 'green'
    statusEle.innerText = 'Rates Added Successfully....'
  } catch(err){
    statusEle.style.color = 'red'
    statusEle.innerText = 'Some Error Occured Please try again after sometime....'
  }
}

const getFreightLookSurchargeRates = async ()=> {
  const statusEle = document.getElementById('status')
  statusEle.innerText = 'Adding Freight Look Surcharge Rates Please wait....'
  try {
    const response = await getFromWebPage('freight_look')
    await sendRatesToRMS({ rates: (response || {}).rates || [], destination: (response || {}).destination, commodity:(response || {}).commodity }, 'create_freight_look_surcharge_rates')
    statusEle.style.color = 'green'
    statusEle.innerText = 'Surcharge Rates Added Successfully....'
  } catch(err){
    statusEle.style.color = 'red'
    statusEle.innerText = 'Some Error Occured Please try again after sometime....'
  }
}

document.getElementById("get_freight_look_rates").addEventListener("click", getFreightLookRates);
document.getElementById("get_new_max_rates").addEventListener("click", getNewMaxRates);
document.getElementById("get_web_cargo_rates").addEventListener("click", getWebCargoRates);
document.getElementById("freight_look_surcharge_rates").addEventListener("click",getFreightLookSurchargeRates)

