import {NgModule} from '@angular/core';
import {TranslateLoader, TranslateModule} from '@ngx-translate/core';
import {HomePage} from 'src/app/home/home.page';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {IonicModule} from '@ionic/angular';
import {RouterModule} from '@angular/router';
import {HttpClient} from "@angular/common/http";
import {HelperService} from "src/app/helper.service";


@NgModule({
    declarations: [
        HomePage,
    ],
    entryComponents: [],
    imports: [
        CommonModule,
        FormsModule,
        IonicModule,
        RouterModule.forChild([
            {
                path: '',
                component: HomePage
            }
        ]),
        TranslateModule.forChild({
            loader: {
                provide: TranslateLoader,
                useFactory: (HelperService.createTranslateLoader),
                deps: [HttpClient]
            }
        })
    ],
    exports: [
        HomePage
    ]
})
export class HomePageModule {
}
