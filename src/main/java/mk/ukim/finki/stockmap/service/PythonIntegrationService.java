package mk.ukim.finki.stockmap.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

@Service
public class PythonIntegrationService {

    private static final String PYTHON_API_URL = "http://localhost:5000/generate-technical-indicators";

    public String generateTechnicalIndicators() {
        RestTemplate restTemplate = new RestTemplate();

        ResponseEntity<String> response = restTemplate.getForEntity(PYTHON_API_URL, String.class);


        String responseBody = response.getBody();

        try {

            JsonNode root = new ObjectMapper().readTree(responseBody);
            JsonNode plots = root.path("plots");


            StringBuilder plotUrls = new StringBuilder();
            for (JsonNode plot : plots) {
                plotUrls.append(plot.asText()).append("\n");
            }

            return plotUrls.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return "Error parsing Python API response";
        }
    }
}
