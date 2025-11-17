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
