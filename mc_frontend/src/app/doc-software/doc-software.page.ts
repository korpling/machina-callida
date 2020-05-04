import {Component, OnInit} from '@angular/core';
import {HelperService} from 'src/app/helper.service';
import {NavController} from '@ionic/angular';
import {HttpClient} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';
import configMC from 'src/configMC';

@Component({
    selector: 'app-doc-software',
    templateUrl: './doc-software.page.html',
    styleUrls: ['./doc-software.page.scss'],
})

export class DocSoftwarePage {
    public configMC = configMC;
    public devIndices: number[] = [...Array(13).keys()];

    constructor(public navCtrl: NavController,
                public http: HttpClient,
                public translate: TranslateService,
                public helperService: HelperService) {
    }
}
