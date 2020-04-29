import {Component} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController} from '@ionic/angular';
import {HttpClient} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';

@Component({
    selector: 'app-sources',
    templateUrl: './sources.page.html',
    styleUrls: ['./sources.page.scss'],
})

export class SourcesPage {

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public translate: TranslateService,
                public helperService: HelperService) {
    }
}
