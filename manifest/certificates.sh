#Create a CA
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "/CN=MyRootCA" -days 3650 -out ca.crt

#Generate server certificate (for Istio Gateway):
openssl genrsa -out server.key 2048
openssl req -new -key server.key -subj "/CN=supplier.zitaconseil.fr" -out server.csr
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

#Generate client certificate (for Postman/curl):
openssl genrsa -out client.key 2048
openssl req -new -key client.key -subj "/CN=myclient" -out client.csr
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365

k create secret generic supplier-credential-mutual-tls --from-file=tls.crt=server.crt --from-file=tls.key=server.key --from-file=ca.crt=ca.crt --dry-run=client -o yaml > supplier-credential-mutual-tls.yaml


#Generate Web client auth certificate

#Generate ca key
#openssl genrsa -out ca-client.key 4096

#Generate ca crt auto signé
#openssl req -x509 -new -nodes -key ca-client.key -sha256 -days 3650 -subj "/CN=CA-CLIENT"   -out ca-client.crt

#Generate client key
#openssl genrsa -out client.key 4096

#Generate csr client
#openssl req -new -key client.key -out client.csr -subj "/CN=wcs-client"

#Generate client.crt
#openssl x509 -req -in client.csr -CA ca-client.crt -CAkey ca-client.key -CAcreateserial -out client.crt -days 36500 -sha256 -extfile client.ext -extensions v3_req

#openssl x509 -in client.crt -text | grep -A4 "Extended Key Usage"

