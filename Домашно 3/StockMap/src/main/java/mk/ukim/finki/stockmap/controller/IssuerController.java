package mk.ukim.finki.stockmap.controller;

import mk.ukim.finki.stockmap.model.CsvData;
import mk.ukim.finki.stockmap.service.IssuerService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.stream.Collectors;

@Controller
public class IssuerController {

    @Autowired
    private IssuerService csvDataService;

    private List<CsvData> allData;

    @GetMapping("/")
    public String index(Model model) {
        allData = csvDataService.readCsvData();


        List<String> issuers = allData.stream()
                .map(CsvData::getIssuer)
                .distinct()
                .sorted()
                .collect(Collectors.toList());

        model.addAttribute("issuers", issuers);
        return "issuerData";
    }


    @PostMapping("/filter")
    public String filterData(@RequestParam("issuer") String issuer, Model model) {
        List<CsvData> filteredData = allData.stream()
                .filter(data -> data.getIssuer().equals(issuer))
                .collect(Collectors.toList());

        List<String> dates = filteredData.stream()
                .map(CsvData::getDate)
                .collect(Collectors.toList());

        List<String> closingPrices = filteredData.stream()
                .map(CsvData::getClose)
                .collect(Collectors.toList());




        model.addAttribute("dates", dates);
        model.addAttribute("closingPrices", closingPrices);
        model.addAttribute("filteredData", filteredData);
        model.addAttribute("issuers", allData.stream()
                .map(CsvData::getIssuer)
                .distinct()
                .sorted()
                .collect(Collectors.toList()));
        return "issuerData";
    }

    @GetMapping("/home")
    public String loadHomePage() {
        return "home";
    }


    @GetMapping("/aboutUs")
    public String loadAboutUsPage() {
        return "aboutUs";
    }
}



