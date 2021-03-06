import {Component, OnInit} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController} from '@ionic/angular';
import {HttpClient} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';
import configMC from '../../configMC';

@Component({
    selector: 'app-imprint',
    templateUrl: './imprint.page.html',
    styleUrls: ['./imprint.page.scss'],
})

export class ImprintPage {
    public configMC = configMC;

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public translate: TranslateService,
                public helperService: HelperService) {
    }
}
