const sendRatesToRMS = async (data={})=> {
  console.log(data)
  const url = 'http://localhost:8000/fcl_freight_rate/create_freight_look_rates'
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data)
  });
  const jsonData = await response.json();
  console.log(jsonData);
}

const getFromWebPage = async () => {
  const [tab] = await chrome.tabs.query({active: true });
  const response = await chrome.tabs.sendMessage(tab.id, { rates: true });
  // do something with response here, not outside the function
  return response
}

const getRates = async ()=> {
  const response = await getFromWebPage()
  console.log(response)
  await sendRatesToRMS({ rates: (response || {}).rates || [], destination: (response || {}).destination })
}

document.getElementById("getrates").addEventListener("click", getRates);

