
build:
	mkdir -p ./dist/
	#pip install -r requirements.txt ./libs/
	cd src/ && zip -qr ../dist/streaming_pipeline.zip .
