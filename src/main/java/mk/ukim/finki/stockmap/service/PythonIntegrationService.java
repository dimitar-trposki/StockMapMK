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
        // Повикај ја Flask апликацијата
        ResponseEntity<String> response = restTemplate.getForEntity(PYTHON_API_URL, String.class);

        // Претвори го JSON одговорот во JsonNode за лесно да се обработи
        String responseBody = response.getBody();

        try {
            // Парсирај го JSON одговорот
            JsonNode root = new ObjectMapper().readTree(responseBody);
            JsonNode plots = root.path("plots");

            // Обработи патеките за графици (на пример, да ги прикажеш во интерфејсот)
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
