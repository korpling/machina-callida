import {NavController} from '@ionic/angular';
import {CorpusMC} from 'src/app/models/corpusMC';
import {Component} from '@angular/core';
import {TranslateService} from '@ngx-translate/core';
import {HelperService} from '../helper.service';
import {CorpusService} from 'src/app/corpus.service';
import {HttpClient} from '@angular/common/http';
import configMC from '../../configMC';

@Component({
    selector: 'app-author-detail',
    templateUrl: './author-detail.page.html',
    styleUrls: ['./author-detail.page.scss'],
})
export class AuthorDetailPage {

    constructor(public navCtrl: NavController,
                public corpusService: CorpusService,
                public translate: TranslateService,
                public http: HttpClient,
                public helperService: HelperService) {
    }

    showPossibleReferences(corpus: CorpusMC) {
        this.corpusService.setCurrentCorpus(corpus);
        this.helperService.goToPage(this.navCtrl, configMC.pageUrlTextRange).then();
    }
}
