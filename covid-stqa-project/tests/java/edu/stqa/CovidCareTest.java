package edu.stqa;

import java.time.Duration;
import java.util.UUID;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class CovidCareTest {
  private WebDriver driver;
  private WebDriverWait wait;
  private final String base = System.getProperty("baseUrl", "http://127.0.0.1:8000");

  @BeforeMethod public void setUp() {
    ChromeOptions options = new ChromeOptions();
    options.addArguments("--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1365,900");
    driver = new ChromeDriver(options);
    wait = new WebDriverWait(driver, Duration.ofSeconds(8));
  }
  @AfterMethod(alwaysRun=true) public void tearDown() { if (driver != null) driver.quit(); }

  @Test public void homeAndDashboardAreAvailable() {
    driver.get(base);
    Assert.assertTrue(driver.getTitle().contains("CovidCare"));
    driver.findElement(By.linkText("Dashboard")).click();
    wait.until(ExpectedConditions.urlContains("dashboard"));
    Assert.assertTrue(driver.getPageSource().contains("Maharashtra"));
  }

  @Test public void registrationRejectsMalformedPhone() {
    driver.get(base + "/?page=register");
    driver.findElement(By.name("name")).sendKeys("STQA User");
    driver.findElement(By.name("email")).sendKeys("qa" + UUID.randomUUID().toString().replace("-", "") + "@example.test");
    driver.findElement(By.name("phone")).sendKeys("12345");
    driver.findElement(By.name("password")).sendKeys("StrongPass1");
    Assert.assertFalse((Boolean)((org.openqa.selenium.JavascriptExecutor)driver)
        .executeScript("return arguments[0].checkValidity()", driver.findElement(By.name("phone"))));
  }

  @Test public void newUserCanRegisterAndSignIn() {
    String email = "qa" + UUID.randomUUID().toString().replace("-", "") + "@example.test";
    String password = "StrongPass1";
    driver.get(base + "/?page=register");
    driver.findElement(By.name("name")).sendKeys("QA " + UUID.randomUUID());
    driver.findElement(By.name("email")).sendKeys(email);
    driver.findElement(By.name("phone")).sendKeys("9876543210");
    driver.findElement(By.name("password")).sendKeys(password);
    driver.findElement(By.cssSelector("button.button")).click();
    wait.until(ExpectedConditions.urlContains("login"));
    driver.findElement(By.name("email")).sendKeys(email);
    driver.findElement(By.name("password")).sendKeys(password);
    driver.findElement(By.cssSelector("button.button")).click();
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".textbutton")));
    Assert.assertTrue(driver.getPageSource().contains("Welcome"));
  }

  @Test public void reportSearchRequiresAuthentication() {
    driver.get(base + "/?page=search");
    Assert.assertTrue(driver.getPageSource().contains("Sign in to search reports"));
  }

  @Test public void adminLoginRejectsInvalidCredentials() {
    driver.get(base + "/?page=admin-login");
    driver.findElement(By.name("email")).sendKeys("admin@example.com");
    driver.findElement(By.name("password")).sendKeys("wrong-password");
    driver.findElement(By.cssSelector("button.button")).click();
    wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[role=alert]")));
    Assert.assertTrue(driver.findElement(By.cssSelector("[role=alert]")).getText().contains("incorrect"));
  }

  @Test public void administratorCanOpenReportList() {
    driver.get(base + "/?page=admin-login");
    driver.findElement(By.name("email")).sendKeys(System.getenv().getOrDefault("ADMIN_EMAIL", "admin@example.com"));
    driver.findElement(By.name("password")).sendKeys(System.getenv().getOrDefault("ADMIN_PASSWORD", "ChangeMe123!"));
    driver.findElement(By.cssSelector("button.button")).click();
    wait.until(ExpectedConditions.urlContains("admin"));
    Assert.assertTrue(driver.getPageSource().contains("Testing reports"));
    Assert.assertTrue(driver.getPageSource().contains("COVID-2026-0001"));
  }
}
