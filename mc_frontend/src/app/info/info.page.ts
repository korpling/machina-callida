import {Component} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController} from '@ionic/angular';
import {HttpClient} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';

@Component({
    selector: 'app-info',
    templateUrl: './info.page.html',
    styleUrls: ['./info.page.scss'],
})

export class InfoPage {
    studiesIndices: number[] = [...Array(4).keys()];

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public translate: TranslateService,
                public helperService: HelperService) {
    }
}
