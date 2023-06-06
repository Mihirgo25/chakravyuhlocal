const sendRatesToRMS = async (data={})=> {
  const url = 'http://localhost:8000/fcl_freight_rate/create_freight_look_rates'
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data)
  });
  await response.json();
}

const getFromWebPage = async () => {
  const [tab] = await chrome.tabs.query({active: true });
  const response = await chrome.tabs.sendMessage(tab.id, { rates: true });
  // do something with response here, not outside the function
  return response
}

const getRates = async ()=> {
  const statusEle = document.getElementById('status')
  statusEle.innerText = 'Adding Rates Please wait....'
  try {
    const response = await getFromWebPage()
    await sendRatesToRMS({ rates: (response || {}).rates || [], destination: (response || {}).destination })
    statusEle.style.color = 'green'
    statusEle.innerText = 'Rates Added Successfully....'
  } catch(err){
    statusEle.style.color = 'red'
    statusEle.innerText = 'Some Error Occured Please try again after sometime....'
  }
}

document.getElementById("getrates").addEventListener("click", getRates);

