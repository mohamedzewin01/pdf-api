<?php
/**
 * PHP Client for PDF AI Question API
 * Usage example for calling the deployed Google Cloud API
 */

class PDFAIClient {
    private $api_base_url;
    
    public function __construct($api_base_url) {
        $this->api_base_url = rtrim($api_base_url, '/');
    }
    
    /**
     * Upload a PDF file to the API
     */
    public function uploadPDF($pdf_file_path) {
        if (!file_exists($pdf_file_path)) {
            return ['error' => 'PDF file not found'];
        }
        
        $curl = curl_init();
        
        $cfile = new CURLFile($pdf_file_path, 'application/pdf', basename($pdf_file_path));
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->api_base_url . '/upload_pdf/',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => ['file' => $cfile],
            CURLOPT_TIMEOUT => 120, // 2 minutes timeout for processing
        ]);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($response === false) {
            return ['error' => 'Failed to connect to API'];
        }
        
        $result = json_decode($response, true);
        $result['http_code'] = $http_code;
        
        return $result;
    }
    
    /**
     * Ask a question about the uploaded PDF
     */
    public function askQuestion($question) {
        $curl = curl_init();
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->api_base_url . '/ask/',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => ['question' => $question],
            CURLOPT_TIMEOUT => 60,
        ]);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($response === false) {
            return ['error' => 'Failed to connect to API'];
        }
        
        $result = json_decode($response, true);
        $result['http_code'] = $http_code;
        
        return $result;
    }
    
    /**
     * Check API health
     */
    public function checkHealth() {
        $curl = curl_init();
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->api_base_url . '/health',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10,
        ]);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($response === false) {
            return ['error' => 'Failed to connect to API'];
        }
        
        $result = json_decode($response, true);
        $result['http_code'] = $http_code;
        
        return $result;
    }
    
    /**
     * Get system status
     */
    public function getStatus() {
        $curl = curl_init();
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->api_base_url . '/status/',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10,
        ]);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($response === false) {
            return ['error' => 'Failed to connect to API'];
        }
        
        $result = json_decode($response, true);
        $result['http_code'] = $http_code;
        
        return $result;
    }
    
    /**
     * Reset the system (clear uploaded document)
     */
    public function resetSystem() {
        $curl = curl_init();
        
        curl_setopt_array($curl, [
            CURLOPT_URL => $this->api_base_url . '/reset/',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CUSTOMREQUEST => 'DELETE',
            CURLOPT_TIMEOUT => 10,
        ]);
        
        $response = curl_exec($curl);
        $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);
        
        if ($response === false) {
            return ['error' => 'Failed to connect to API'];
        }
        
        $result = json_decode($response, true);
        $result['http_code'] = $http_code;
        
        return $result;
    }
}

// Example usage:
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    // Replace with your deployed Google Cloud URL
    $api_url = 'https://your-project-id.appspot.com';
    $client = new PDFAIClient($api_url);
    
    // Example 1: Check health
    echo "=== Checking API Health ===\n";
    $health = $client->checkHealth();
    print_r($health);
    
    // Example 2: Upload PDF (replace with actual PDF path)
    /*
    echo "\n=== Uploading PDF ===\n";
    $upload_result = $client->uploadPDF('/path/to/your/document.pdf');
    print_r($upload_result);
    
    if (isset($upload_result['message']) && $upload_result['http_code'] == 200) {
        // Example 3: Ask question
        echo "\n=== Asking Question ===\n";
        $question_result = $client->askQuestion('What is this document about?');
        print_r($question_result);
    }
    */
}
?>
