package mk.ukim.finki.stockmap.controller;

import mk.ukim.finki.stockmap.model.CsvData;
import mk.ukim.finki.stockmap.service.IssuerService;
import mk.ukim.finki.stockmap.service.PythonIntegrationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
@Controller
@RequestMapping("/analysis")
public class AnalysisController {

    @GetMapping("/generate")
    public String generateTechnicalIndicators(@RequestParam String issuer, Model model) {
        List<String> plotPaths = new ArrayList<>();
        List<String> tablePaths = new ArrayList<>();
        try {
            String scriptPath = "src/main/java/technical_analysis.py";
            String csvPath = "src/main/java/stock_data.csv";
            String outputPath = "src/main/resources/static/" + issuer + "_tables";

            ProcessBuilder processBuilder = new ProcessBuilder("python", scriptPath, issuer, csvPath,outputPath);
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

        model.addAttribute("plotPaths", plotPaths);
        model.addAttribute("tablePaths",tablePaths);
        System.out.println(plotPaths);
        System.out.println(tablePaths);
        return "technical";
    }
}

