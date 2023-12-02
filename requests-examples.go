package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

type RequestData struct {
	Query string `json:"query"`
}

func main() {
	// Define the API endpoint and API key
	apiURL := "https://api.runpod.io/graphql?api_key=HFAAGI80CN15TJTC249NKHTOBW5CNH2H58GNGMQ6"

	requestData := RequestData{
		Query: `mutation { podFindAndDeployOnDemand( input: {
            cloudType: SECURE,
            gpuCount: 1,
            volumeInGb: 0,
            containerDiskInGb: 40,
            gpuTypeId: "NVIDIA RTX A5000",
            name: "RunPod Tensorflow",
            imageName: "lenslessai/server-kohya:0.0.13",
            env: [
                { key: "STEPS_PER_IMAGE", value: "1" },
                { key: "EPOCHS", value: "1" },
                { key: "KIND", value: "man" },
                { key: "AWS_SECRET_KEY", value: "Of1vmY0Y4iucckbGoQil0sk6pk0C7YKauxGWB1sN" },
                { key: "AWS_ACCESS_KEY", value: "AKIA5UTHMH6PCXXI7PGO" },
                { key: "PHOTOS_BUCKET", value: "lenslessai-photos" },
                { key: "PHOTOS_DIRECTORY", value: "samir/123" },
                { key: "MODELS_BUCKET", value: "lenslessai-models" },
                { key: "MODELS_DIRECTORY", value: "samir/models" },
                { key: "CROPPED_PHOTOS_BUCKET", value: "lenslessai-cropped-photos" },
                { key: "MODEL_NAME", value: "20_images_25_steps_6_epochs" },
                { key: "ENABLE_BUCKET", value: "false" }
            ]
        } ) { id imageName env machineId machine { podHostId } } }`,
	}

	// Convert the requestData struct to JSON
	requestDataBytes, err := json.Marshal(requestData)
	if err != nil {
		fmt.Println("Error marshaling JSON:", err)
		return
	}

	// Log the request payload
	fmt.Println("Request Payload:")
	fmt.Println(string(requestDataBytes))
	// Create a HTTP POST request
	req, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(requestDataBytes))
	if err != nil {
		fmt.Println("Error creating request:", err)
		return
	}

	// Set the Content-Type header
	req.Header.Set("Content-Type", "application/json")

	// Create an HTTP client and send the request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending request:", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Request failed with status code: %d\n", resp.StatusCode)
	}

	// Read and print the response
	var responseJSON map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&responseJSON)
	if err != nil {
		fmt.Println("Error decoding response:", err)
		return
	}

	fmt.Printf("Response: %+v\n", responseJSON)
}
