import {Component} from '@angular/core';
import {StatusBar} from '@ionic-native/status-bar/ngx';
import {Config, MenuController, NavController, Platform} from '@ionic/angular';
import {SplashScreen} from '@ionic-native/splash-screen/ngx';
import {TranslateService} from '@ngx-translate/core';
import {HelperService} from 'src/app/helper.service';
import configMC from '../configMC';
import {CorpusService} from './corpus.service';

@Component({
    selector: 'app-root',
    templateUrl: 'app.component.html'
})
export class AppComponent {
    public configMC = configMC;

    constructor(platform: Platform,
                public statusBar: StatusBar,
                public translate: TranslateService,
                private config: Config,
                private splashScreen: SplashScreen,
                public helperService: HelperService,
                public navCtrl: NavController,
                public menuCtrl: MenuController,
                public corpusService: CorpusService,
    ) {
        platform.ready().then(() => {
            this.corpusService.initCorpusService().then();
            // Okay, so the platform is ready and our plugins are available.
            // Here you can do any higher level native things you might need.
            this.statusBar.styleDefault();
            this.splashScreen.hide();
        });
        this.initTranslate();
    }

    closeMenu(result: boolean) {
        this.menuCtrl.close(configMC.menuId).then();
    }

    initTranslate() {
        // Set the default language for translation strings, and the current language.
        this.translate.setDefaultLang('en');

        if (this.translate.getBrowserLang() !== undefined) {
            this.translate.use(this.translate.getBrowserLang());
        } else {
            this.translate.use(this.translate.getDefaultLang()); // Set your language here
        }
        // for testing purposes
        // this.translate.use('de');

        // this.translate.get(['BACK_BUTTON_TEXT']).subscribe(values => {
        //     this.config.set('backButtonText', values.BACK_BUTTON_TEXT); // 'ios',
        // });
    }
}
