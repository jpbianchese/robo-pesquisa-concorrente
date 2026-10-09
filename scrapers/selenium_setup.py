#iniciar
import undetected_chromedriver as uc

def iniciar_driver():
  
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')

    
    driver = uc.Chrome(options=options, version_main=154)
    
    return driver