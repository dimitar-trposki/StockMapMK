package mk.ukim.finki.microserviceanalysis.controller;

import org.springframework.web.bind.annotation.*;
import java.io.*;
import java.util.*;

@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    @GetMapping("/generate")
    public Map<String, Object> generateTechnicalIndicators(@RequestParam String issuer) {
        List<String> plotPaths = new ArrayList<>();
        List<String> tablePaths = new ArrayList<>();
        Map<String, Object> response = new HashMap<>();

        try {
            String scriptPath = "scripts/technical_analysis.py";
            String csvPath = "scripts/stock_data.csv";
            String outputPath = "src/main/resources/static/" + issuer + "_tables";

            ProcessBuilder processBuilder = new ProcessBuilder("python", scriptPath, issuer, csvPath, outputPath);
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));

            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("Python Output: " + line);
                if (line.endsWith(".png")) {
                    plotPaths.add("/" + issuer + "_tables/" + line.trim());
                } else if (line.endsWith(".html")) {
                    tablePaths.add("/" + issuer + "_tables/" + line.trim());
                }
            }

            String errorLine;
            while ((errorLine = errorReader.readLine()) != null) {
                System.err.println("Python Error: " + errorLine);
            }

            process.waitFor();
        } catch (Exception e) {
            e.printStackTrace();
        }

        response.put("plotPaths", plotPaths);
        response.put("tablePaths", tablePaths);
        return response;
    }
}