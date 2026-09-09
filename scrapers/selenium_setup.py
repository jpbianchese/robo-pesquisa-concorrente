#iniciar
import undetected_chromedriver as uc

def iniciar_driver():
  
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")

    
    driver = uc.Chrome(options=options, version_main=152)
    
    return driver