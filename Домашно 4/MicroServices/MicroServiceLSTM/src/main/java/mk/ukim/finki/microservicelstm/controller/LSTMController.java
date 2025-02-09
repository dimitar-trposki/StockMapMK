package mk.ukim.finki.microservicelstm.controller;

import org.springframework.stereotype.Controller;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
@RequestMapping({"/lstm"})
public class LSTMController {
    public LSTMController() {
    }

    @GetMapping({"/prediction"})
    public String generateTechnicalIndicators(@RequestParam String issuer, Model model) {
        List<String> plotPaths = new ArrayList();
        List<Map<String, String>> forecastData = new ArrayList();

        try {
            String scriptPath = "src/main/java/LSTM.py";
            String csvPath = "src/main/java/stock_data.csv";
            String outputPath = "src/main/resources/static/" + issuer + "_lstm";
            ProcessBuilder processBuilder = new ProcessBuilder(new String[]{"python", scriptPath, csvPath, outputPath, issuer});
            Process process = processBuilder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));

            String line;
            String forecastTablePath;
            while((line = reader.readLine()) != null) {
                System.out.println("Python Output: " + line);
                if (line.endsWith(".png")) {
                    plotPaths.add(line.trim());
                } else if (line.endsWith(".csv")) {
                    forecastTablePath = "src/main/resources/static/" + line.trim();
                    forecastData = this.readForecastData(forecastTablePath);
                }
            }

            while((forecastTablePath = errorReader.readLine()) != null) {
                System.err.println("Python Error: " + forecastTablePath);
            }

            process.waitFor();
        } catch (Exception var14) {
            var14.printStackTrace();
        }

        model.addAttribute("plotPaths", plotPaths);
        model.addAttribute("forecastData", forecastData);
        System.out.println("Plot Paths: " + String.valueOf(plotPaths));
        System.out.println("Forecast Data: " + String.valueOf(forecastData));
        return "lstm";
    }

    private List<Map<String, String>> readForecastData(String forecastTablePath) {
        List<Map<String, String>> data = new ArrayList();

        try {
            BufferedReader br = new BufferedReader(new FileReader(forecastTablePath));

            try {
                String[] headers = br.readLine().split(",");

                String line;
                while((line = br.readLine()) != null) {
                    String[] values = line.split(",");
                    Map<String, String> row = new LinkedHashMap();

                    for(int i = 0; i < headers.length; ++i) {
                        row.put(headers[i], values[i]);
                    }

                    data.add(row);
                }
            } catch (Throwable var10) {
                try {
                    br.close();
                } catch (Throwable var9) {
                    var10.addSuppressed(var9);
                }

                throw var10;
            }

            br.close();
        } catch (IOException var11) {
            var11.printStackTrace();
        }

        return data;
    }
}