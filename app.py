from flask import Flask, request, Response, session, redirect, render_template_string
import xml.etree.ElementTree as ET
import uuid
import datetime
import html
import os

app = Flask(__name__)
app.secret_key = 'your-super-secret-key'

# Simulated session store (in-memory for demo)
punchout_sessions = {}

@app.route('/punchout/start', methods=['POST','GET'])
def punchout_start():
    try:
        tree = ET.fromstring(request.data)
        buyer_cookie = tree.find('.//BuyerCookie').text
        return_url = tree.find('.//BrowserFormPost/URL').text
        sender_id = tree.find('.//Sender/Credential/Identity').text
        shared_secret = tree.find('.//Sender/Credential/SharedSecret').text

        # Simulate auth check
        if shared_secret != 'abc123':
            return Response('Unauthorized', status=401)

        session_id = str(uuid.uuid4())
        punchout_sessions[session_id] = {
            'buyer_cookie': buyer_cookie,
            'return_url': return_url,
            'sender_id': sender_id,
            'created_at': datetime.datetime.utcnow()
        }

        
        STORE_URL = os.environ.get("STORE_URL", "http://localhost:5000/punchout/store")
        response_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<cXML payloadID="{uuid.uuid4()}" timestamp="{datetime.datetime.utcnow().isoformat()}Z">
  <Response>
    <Status code="200" text="OK" />
    <PunchOutSetupResponse>
      <StartPage>
        <URL>{STORE_URL}?session_id={session_id}</URL>
      </StartPage>
    </PunchOutSetupResponse>
  </Response>
</cXML>
'''
        return Response(response_xml, content_type='text/xml')
    except Exception as e:
        return Response(str(e), status=500)

@app.route('/punchout/store')
def punchout_store():
    session_id = request.args.get('session_id')
    if session_id not in punchout_sessions:
        return 'Invalid session', 403

    return render_template_string('''
        <h2>Supplier Store Demo</h2>
        <p>Session ID: {{ session_id }}</p>
        <p>Welcome to the PunchOut Store! You can add items to your cart.</p>
        <p>Click "Return Cart" to send the cart back to your ERP system.</p>
        <p>For demo purposes, we will simulate adding a product to the cart.</p
        <form method="POST" action="/punchout/cart">
            <input type="hidden" name="session_id" value="{{ session_id }}">
            <input type="text" name="product_id" value="12345">
            <input type="text" name="description" value="Laser Printer">
            <input type="number" name="quantity" value="1">
            <input type="text" name="price" value="259.99">
            <input type="submit" value="Return Cart">
        </form>
    ''', session_id=session_id)

@app.route('/punchout/cart', methods=['POST'])
def punchout_cart():
    session_id = request.form.get('session_id')
    if session_id not in punchout_sessions:
        return 'Invalid session', 403

    session_data = punchout_sessions[session_id]
    buyer_cookie = session_data['buyer_cookie']
    return_url = session_data['return_url']

    # Construct PunchOutOrderMessage
    response_xml = f'''
    <cXML payloadID="{uuid.uuid4()}" timestamp="{datetime.datetime.utcnow().isoformat()}Z">
      <Message>
        <PunchOutOrderMessage>
          <BuyerCookie>{buyer_cookie}</BuyerCookie>
          <PunchOutOrderMessageHeader operationAllowed="create">
            <Total>
              <Money currency="EUR">{request.form['price']}</Money>
            </Total>
          </PunchOutOrderMessageHeader>
          <ItemIn quantity="{request.form['quantity']}">
            <ItemID>
              <SupplierPartID>{request.form['product_id']}</SupplierPartID>
            </ItemID>
            <ItemDetail>
              <UnitPrice>
                <Money currency="EUR">{request.form['price']}</Money>
              </UnitPrice>
              <Description xml:lang="en">{request.form['description']}</Description>
              <UnitOfMeasure>EA</UnitOfMeasure>
              <Classification domain="UNSPSC">43212105</Classification>
            </ItemDetail>
          </ItemIn>
        </PunchOutOrderMessage>
      </Message>
    </cXML>
    '''

    escaped_xml = html.escape(response_xml)
    # For demo, just display it
    return f"<h2>Returning Cart to ERP</h2>\
    <div style=\"white-space: pre; font-family: monospace; border: 1px solid #ccc; padding: 1em; background-color: #f8f8f8;\">{ escaped_xml }</div> \
    <form method=\"POST\" action=\"{return_url}\">\
    <input name=\"cxml\" type=\"hidden\" rows=20 cols=100 value=\"{escaped_xml}\"></input>\
    <br/><br/><input type=\"submit\" value=\"Return Cart\">\
    <input type=\"hidden\" name=\"buyer_cookie\" value=\"{buyer_cookie}\">\
    </form>\
    <br><p>Would POST to: {return_url}</p>"

if __name__ == '__main__':
    app.run(debug=True)
